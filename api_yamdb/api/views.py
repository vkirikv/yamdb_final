# api_yamdb/api/views.py
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.filters import TitlesFilters
from reviews.models import Category, Comment, Genre, Review, Title, User
from .mixins import CreateListDestroyViewSet
from .permissions import (
    AdminPermission,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModeratorOrReadOnly
)
from .serializers import AdminSerializer, CategorySerializer, GenreSerializer
from .serializers import CommentSerializer, GetConfirmationCodeSerializer
from .serializers import MeSerializer, ReviewSerializer, SignupSerializer
from .serializers import TitleReadSerializer, TitleWriteSerializer
from .serializers import TokenSerializer

GET_POST_USER_LIST = {'get': 'list',
                      'post': 'create'
                      }
GET_PATCH_DELETE_USER_DETAIL = {'get': 'retrieve',
                                'patch': 'partial_update',
                                'delete': 'destroy'
                                }
GET_PATCH__USER_ME = {'get': 'retrieve',
                      'patch': 'partial_update'
                      }


class APISignup(APIView):
    """Самостоятельная регистрация пользователей."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data,)
        if serializer.is_valid():
            serializer.save()
            username = serializer.data['username']
            email = serializer.data['email']
            user = get_object_or_404(User, username=username)
            confirmation_code = user.confirmation_code
            send_mail('Код подтверждения',
                      f'{confirmation_code}',
                      'yamdb.com',
                      [f'{email}']
                      )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        serializer = GetConfirmationCodeSerializer(user, data=request.data,
                                                   partial=True)
        if serializer.is_valid():
            serializer.save()
            username = serializer.data['username']
            email = serializer.data['email']
            user = get_object_or_404(User, username=username)
            confirmation_code = user.confirmation_code
            send_mail('Код подтверждения',
                      f'{confirmation_code}',
                      'yamdb.com',
                      [f'{email}']
                      )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_tokens_for_user(user):
    """Получение токена."""
    refresh = RefreshToken.for_user(user)

    data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return data


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_token(request):
    """Получение токена пользователем."""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Работа администратора с пользователями."""

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (AdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = "username"


user_list = UserViewSet.as_view(GET_POST_USER_LIST)
user_detail = UserViewSet.as_view(GET_PATCH_DELETE_USER_DETAIL)


class MeViewSet(viewsets.ModelViewSet):
    """Получение и изменение своих данных пользователями."""

    serializer_class = MeSerializer

    def update(self, request, *args, **kwargs):
        pk = request.user.pk
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = request.user.pk
        user = get_object_or_404(User, pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


user_me = MeViewSet.as_view(GET_PATCH__USER_ME)


class CategoryViewSet(CreateListDestroyViewSet):
    """Работает со списком категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (
        IsAdminOrReadOnly,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Работает со списком жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (
        IsAdminOrReadOnly,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Работает со списком произведений."""

    queryset = Title.objects.prefetch_related(
        'category', 'genre').annotate(
            rating=Avg('reviews__score'))
    permission_classes = (
        IsAdminOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilters

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Обрабатывает отзывы к произведениям."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorOrAdminOrModeratorOrReadOnly,
    )

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Обрабатывает комментарии к отзывам на произведения."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorOrAdminOrModeratorOrReadOnly,
    )

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
