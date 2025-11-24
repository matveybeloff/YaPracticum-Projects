from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.utils.images import decode_data_uri_image
from api.recipes.serializers import RecipeMinifiedSerializer
from recipes.models import Recipe
from users.models import Subscription

User = get_user_model()


AVATAR_ALLOWED_MIME = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and getattr(request, "user", None)
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        url = obj.avatar.url
        return request.build_absolute_uri(url) if request else url


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        request = self.context.get("request")
        qs = Recipe.objects.filter(author=obj).order_by("-id")
        limit = request.query_params.get("recipes_limit") if request else None
        if limit and limit.isdigit():
            n = int(limit)
            if n >= 0:
                qs = qs[: n]
        return RecipeMinifiedSerializer(
            qs, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SetAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField(write_only=True)

    def validate_avatar(self, value):
        return decode_data_uri_image(
            value,
            prefix="users/",
            allowed_mime=AVATAR_ALLOWED_MIME,
        )

    def save(self, **kwargs):
        user = self.context["request"].user
        file_obj = self.validated_data["avatar"]
        user.avatar.save(file_obj.name, file_obj, save=True)
        self.instance = user
        return user

    def to_representation(self, instance):
        request = self.context.get("request")
        url = (
            instance.avatar.url if getattr(instance, "avatar", None) else None
        )
        return {
            "avatar": (
                request.build_absolute_uri(url) if request and url else url
            )
        }


class SubscriptionWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, attrs):
        user = attrs.get("user")
        author = attrs.get("author")
        if user == author:
            raise serializers.ValidationError(
                {"detail": "Нельзя подписаться на себя."}
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {"detail": "Подписка уже существует."}
            )
        return attrs

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.author, context=self.context
        ).data
