# api_yandb/api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import APISignup, auth_token, user_list, user_detail, user_me
from .views import CategoryViewSet, GenreViewSet, TitleViewSet
from .views import ReviewViewSet, CommentViewSet


router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')
router_v1.register('titles', TitleViewSet, basename='titles')

auth_patterns = [
    path('signup/', APISignup.as_view(), name="signup"),
    path('token/', auth_token, name="token-create"),
]

users_patterns = [
    path('', user_list, name="user-list"),
    path('me/', user_me, name="user-me"),
    path('<str:username>/', user_detail, name="user-detail"),
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/users/', include(users_patterns)),
    path('v1/', include(router_v1.urls)),
]
