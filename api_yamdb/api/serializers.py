from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions, serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(max_value=10, min_value=1)

    class Meta:
        fields = ('id', 'name', 'year',
                  'rating', 'description',
                  'genre', 'category')
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(many=True, queryset=Genre.objects.all(),
                             slug_field='slug')

    category = SlugRelatedField(queryset=Category.objects.all(),
                                slug_field='slug')

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')
        model = Title
        validators = [UniqueTogetherValidator(
            queryset=Title.objects.all(),
            fields=('name', 'category')
        )]

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Проверьте год выпуска произведения! '
                'Он не может быть больше текущего года')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username',
                              read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, data):
        if (self.context.get('request').method == 'POST'
            and Review.objects.filter(
                author=self.context.get('request').user,
                title=self.context.get('view').kwargs.get('title_id')
        ).exists()):
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение')
        return super().validate(data)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserSelfSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('username', 'email', 'role',)


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Укажите username, отличный от me')
        return value


class MyTokenObtainSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['confirmation_code'] = PasswordField()

    def validate(self, attrs):
        self.user = get_object_or_404(
            User,
            username=attrs[self.username_field]
        )
        if self.user is None or not self.user.is_active:
            raise exceptions.ValidationError('Несуществующий пользователь')
        if not default_token_generator.check_token(
            self.user,
            attrs['confirmation_code']
        ):
            raise exceptions.ValidationError('Невалидный код подтверждения')
        return {'access_token': str(AccessToken.for_user(self.user))}
