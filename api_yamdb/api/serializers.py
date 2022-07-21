from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import ROLE_CHOICES, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            "name",
            "slug",
        )


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(required=True, many=True)
    category = CategorySerializer(required=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", many=False, queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )
    title = serializers.SlugRelatedField(
        queryset=Title.objects.all(),
        required=False,
        slug_field="id",
        write_only=True,
    )

    class Meta:
        model = Review
        fields = "__all__"

    def get_title(self):
        return get_object_or_404(
            Title, id=self.context.get("view").kwargs.get("title_id")
        )

    def validate(self, attrs):
        if (
            Review.objects.filter(
                author=self.context["request"].user, title=self.get_title()
            ).exists()
            and self.context["request"].method != "PATCH"
        ):
            raise serializers.ValidationError(
                "Нельзя добавить второй отзыв на произведение"
            )
        return attrs


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Email должен быть уникальным."""
        lower_email = value.lower()
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Email должен быть уникальным")
        return lower_email

    def validate_username(self, value):
        """Использовать имя 'me' в качестве username запрещено."""
        if value.lower() == "me":
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        return value

    class Meta:
        model = User
        fields = (
            "email",
            "username",
        )


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        default="user",
    )

    def validate_email(self, value):
        """Email должен быть уникальным."""
        lower_email = value.lower()
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Email должен быть уникальным")
        return lower_email

    def validate_username(self, value):
        """Использовать имя 'me' в качестве username запрещено."""
        if value.lower() == "me":
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        return value

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserMeSerializer(UserSerializer):
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        read_only=True,
    )


class CustomTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=200,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=200,
        required=True,
    )

    def validate_username(self, value):
        """Пользователь должен существовать, иначе ошибка 404"""
        get_object_or_404(User, username=value.lower())
        return value.lower()

    def validate_confirmation_code(self, value):
        """Валидация confirmation_code"""
        lower_confirmation_code = value.lower()
        if self.initial_data.get("username") is None:
            raise serializers.ValidationError(
                "Нельзя делать запрос без username"
            )
        username = self.initial_data.get("username")
        user = get_object_or_404(User, username=username)
        if not PasswordResetTokenGenerator().check_token(
            user, lower_confirmation_code
        ):
            raise serializers.ValidationError("Неверный код подтверждения")
        return lower_confirmation_code
