from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from reviews.models import (
    User,
    Title,
    Category,
    Comment,
    Genre,
    Review,
)
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueValidator


class UserRegistrationSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    username = serializers.SlugField(required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Запрещенное имя пользователя!')
        return value

    class Meta:
        model = User
        fields = ('email', 'username')


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ['id', 'name', 'year', 'description']


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    def validate_score(self, value):
        if 1 > value > 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Должен быть один отзыв.')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field='text', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[UniqueValidator(User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())],
        required=True,
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User


class UserWithoutRoleSerializer(UserSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User
        read_only_fields = ('role',)
