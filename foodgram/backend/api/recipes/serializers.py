from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.utils.images import decode_data_uri_image
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription


RECIPE_ALLOWED_MIME = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
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
                user=request.user,
                author=obj,
            ).exists()
        )

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        url = obj.avatar.url
        return request.build_absolute_uri(url) if request else url


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source="ingredient_amounts",
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and getattr(request, "user", None)
            and request.user.is_authenticated
            and obj.in_favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and getattr(request, "user", None)
            and request.user.is_authenticated
            and obj.in_carts.filter(user=request.user).exists()
        )

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientAmount
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = serializers.CharField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id",)

    def validate_image(self, value):
        return decode_data_uri_image(
            value,
            prefix="recipes/images/",
            allowed_mime=RECIPE_ALLOWED_MIME,
        )

    def validate_tags(self, tags):
        tag_ids = [getattr(tag, "pk", tag) for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError("Повторяющиеся теги.")
        return tags

    def validate_ingredients(self, ingredients):
        ids = [
            getattr(item.get("ingredient"), "pk", None)
            for item in ingredients
        ]
        if None in ids:
            return ingredients
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({
                "ingredients": ["Ингредиенты не должны повторяться."]
            })
        return ingredients

    def validate(self, attrs):
        is_update = self.instance is not None
        if is_update:
            if "ingredients" not in attrs:
                raise serializers.ValidationError({
                    "ingredients": ["Это поле обязательно."]
                })
            if "tags" not in attrs:
                raise serializers.ValidationError({
                    "tags": ["Ингредиенты не должны повторяться."]
                })

        ingredients = attrs.get("ingredients")
        tags = attrs.get("tags")
        if ingredients is not None and len(ingredients) == 0:
            raise serializers.ValidationError({
                "ingredients": ["Список ингредиентов не может быть пустым."]
            })
        if tags is not None and len(tags) == 0:
            raise serializers.ValidationError({
                "tags": ["Список тегов не может быть пустым."]
            })
        return attrs

    def _apply_ingredients(self, recipe: Recipe, items):
        IngredientAmount.objects.filter(recipe=recipe).delete()
        data = [
            IngredientAmount(
                recipe=recipe,
                ingredient=item["ingredient"],
                amount=item["amount"],
            )
            for item in items
        ]
        IngredientAmount.objects.bulk_create(data)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._apply_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        self._apply_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class _BaseRelationWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    def validate(self, attrs):
        user = attrs.get("user")
        recipe = attrs.get("recipe")
        model = self.Meta.model
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                "detail": "Объект уже существует."
            })
        return attrs

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context,
        ).data


class FavoriteWriteSerializer(_BaseRelationWriteSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")


class ShoppingCartWriteSerializer(_BaseRelationWriteSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
