from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from django.db.models import Avg

from .serializers import get_tokens_for_user, UserRegistrationSerializer
from reviews.models import User, Title, Category, Review, Genre
from .filters import TitleFilter
from .mixins import ModelMixinSet
from .permissions import (
    AdminModeratorAuthorPermission,
    AdminOnly,
    IsAdminUserOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer,
    UserWithoutRoleSerializer,
)
from .utils import (
    validate_request_data,
    send_confirmation_email,
)


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.annotate(rating=Avg('reviews__score'))
        .all()
        .order_by('name')
    )
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AdminModeratorAuthorPermission]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=UserWithoutRoleSerializer,
    )
    def my_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if user.is_user and 'role' in request.data:
                serializer = UserWithoutRoleSerializer(
                    user, data=request.data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    data = request.data
    validate_request_data(data)
    serializer = UserRegistrationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user, created = User.objects.get_or_create(
        username=data['username'], email=data['email']
    )
    send_confirmation_email(user)
    if created:
        return Response(serializer.data, status=status.HTTP_200_OK)
    if not created and not user.activated:
        message = 'Код подтверждения отправлен заново.'
    else:
        message = (
            'Ваша запись уже активна! Код отправлен заново.'
            'Пожалуйста, больше не теряйте его.',
        )
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_token(request):
    for arg in ('username', 'confirmation_code'):
        if not request.data.get(arg):
            return Response(
                {arg: ['Это обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
    user = get_object_or_404(User, username=request.data['username'])
    if default_token_generator.check_token(
        user, token=request.data['confirmation_code']
    ):
        user.is_active = True
        user.save()
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
    return Response(
        f'Неверный код подтверждения: {request.data["confirmation_code"]}\n'
        'Необходимо сгенерировать новый код, или найти правильный.',
        status=status.HTTP_400_BAD_REQUEST,
    )
