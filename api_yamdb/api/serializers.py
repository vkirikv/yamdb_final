# api_yamdb/api/serializers.py
from django.contrib.auth.base_user import BaseUserManager
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from reviews.models import AUTH_USER, Category, ROLES_CHOICES, Comment
from reviews.models import Genre, Review, Title, User


class SignupSerializer(serializers.ModelSerializer):
    """Самостоятельная регистрация пользователей."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if 'me' == username.lower():
            raise serializers.ValidationError(
                'Имя me использовать запрещено!'
            )
        return username

    def create(self, validated_data):
        password = BaseUserManager().make_random_password()
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password,
            confirmation_code=password
        )
        user.save()
        return user


class GetConfirmationCodeSerializer(serializers.Serializer):
    """Получение кода подтверждения при регистрации администратором."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate(self, data):
        email = data['email']
        if not User.objects.filter(email=email):
            raise serializers.ValidationError(
                f'Пользователя c email: {email} не существует!')
        return data

    def update(self, instance, validated_data):
        password = BaseUserManager().make_random_password()
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.password = password
        instance.confirmation_code = password
        instance.save()
        return instance


class TokenSerializer(serializers.ModelSerializer):
    """Получение токена пользователем."""

    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'confirmation_code',
            'username',
        )
        extra_kwargs = {
            'username': {
                'validators': []
            }
        }

    def validate(self, data):
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения!')
        return data


class AdminSerializer(serializers.ModelSerializer):
    """Работа администратора с пользователями."""

    role = serializers.ChoiceField(choices=ROLES_CHOICES, default=AUTH_USER)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class MeSerializer(serializers.ModelSerializer):
    """Получение и изменение своих данных пользователями."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('username', 'role')


class CategorySerializer(serializers.ModelSerializer):
    """Работа с категориями."""

    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Работа с жанрами."""

    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """Получение данных о произведениях."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Изменение данных произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Добавление отзыва к произведению."""

    score = serializers.IntegerField(min_value=1, max_value=10)
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='id')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = int(
            self.context.get('request').parser_context.get('kwargs').
            get('title_id'))
        author_id = self.context.get("request").user.pk
        if Review.objects.filter(
                title_id=title_id,
                author_id=author_id).exists():
            raise serializers.ValidationError('К произведению можно'
                                              ' оставить только один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Добавление комментария к отзыву."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('review',)
        model = Comment
