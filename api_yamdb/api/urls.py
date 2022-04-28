from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       MyTokenObtainView, ReviewViewSet, SignUpView,
                       TitleViewSet, UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='v1_users')
router_v1.register('categories', CategoryViewSet, basename='v1_categories')
router_v1.register('genres', GenreViewSet, basename='v1_genres')
router_v1.register('titles', TitleViewSet, basename='v1_titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='v1_reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='v1_comments'
)
router_v1.register('users', UserViewSet, basename='v1_users')

auth_urls = [
    path(
        'signup/',
        SignUpView.as_view(),
        name='sign_up'
    ),
    path(
        'token/',
        MyTokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_urls))
]
