# api/views.py

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Genre, Review, Title, Category, User

from .filters import TitleFilter
from .permissions import (
    IsAdministratorOrReadOnly, IsAdministrator,
    IsAdministratorModeratorOwnerOrReadOnly
)
from .serializers import (
    CommentSerializer, ReviewSerializer,
    GenreSerializer, CategorySerializer,
    TitleCreateSerializer, TitleGetSerializer,
    TokenObtainSerializer, UserSerializer,
    MeUserSerializer, SignupSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdministratorModeratorOwnerOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdministratorModeratorOwnerOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class MixinGenreAndCategoryViewSet(mixins.CreateModelMixin,
                                   mixins.DestroyModelMixin,
                                   mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    permission_classes = (IsAdministratorOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(MixinGenreAndCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(MixinGenreAndCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleGetSerializer
    permission_classes = (IsAdministratorOrReadOnly,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_class = TitleFilter
    ordering = ('name',)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleCreateSerializer
        return TitleGetSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Регистрация нового пользователя."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, created = User.objects.get_or_create(**serializer.validated_data)
    except Exception:
        return Response(
            {'error': [
                (f'Пользователь с username = {username} '
                 f'и/или email = {email} уже существует!')
            ]},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.confirmation_code = get_random_string(
        length=settings.CONFIRMATION_CODE_LENGTH
    )
    user.save()
    send_mail(
        subject=_("Регистрация пользователя на YaMDb"),
        message=f'{_("Ваш проверочный код")} {user.confirmation_code}.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token(request):
    """Выдача JWT-токена пользователю."""
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = 'confirmation_code'
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    if user.confirmation_code == serializer.validated_data[confirmation_code]:
        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK
        )
    return Response(
        {confirmation_code: [_('Неверный код подтверждения')]},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdministrator,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        url_name='users_detail',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MeUserSerializer,
    )
    def users_detail(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
