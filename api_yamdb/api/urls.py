from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (get_confirmation_code,
                    get_jwt_token,
                    CategoryDetail,
                    CategoryList,
                    CommentViewSet,
                    GenreDetail,
                    GenreList,
                    ReviewViewSet,
                    TitlesViewSet,
                    UsersViewSet,
                    )


router_v1 = DefaultRouter()
router_v1.register(r'titles', TitlesViewSet, basename="titles")
router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
app_name = 'api'

v1_auth_patterns = [
    path('signup/', get_confirmation_code),
    path('token/', get_jwt_token)
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(v1_auth_patterns)),
    path(r'v1/categories/',
         CategoryList.as_view(),
         name='category_list'),
    path(r'v1/categories/<slug:slug>/',
         CategoryDetail.as_view(),
         name='category_detail'),
    path(r'v1/genres/',
         GenreList.as_view(),
         name='genres_list'),
    path(r'v1/genres/<slug:slug>/',
         GenreDetail.as_view(),
         name='genres_detail'),
    path('v1/', include('djoser.urls')),
]
