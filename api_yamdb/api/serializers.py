# api/serialiser.py

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                _('Вы уже написали отзыв к этому произведению.')
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = ('__all__',)


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class MixinValidateUsernameSerializer:

    def validate_username(self, value):
        validate_username(value)
        return value


class MixinUsernameSerializer(serializers.Serializer,
                              MixinValidateUsernameSerializer):
    username = serializers.CharField(max_length=150, required=True)


class SignupSerializer(MixinUsernameSerializer):
    email = serializers.EmailField(max_length=254, required=True)


class TokenObtainSerializer(MixinUsernameSerializer):
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        required=True
    )


class UserSerializer(serializers.ModelSerializer,
                     MixinValidateUsernameSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class MeUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
