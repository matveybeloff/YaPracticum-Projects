from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string

from config.constants import (
    COOKING_TIME_MAX,
    COOKING_TIME_MIN,
    INGREDIENT_AMOUNT_MAX,
    INGREDIENT_AMOUNT_MIN,
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    SHORTLINK_CODE_LENGTH,
    SHORTLINK_CODE_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name="Слаг",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="uniq_ingredient_name_unit",
            ),
        ]
        indexes = [models.Index(fields=("name",), name="ingredient_name_idx")]
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name="Название",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN,
                message=f"Минимум {COOKING_TIME_MIN}",
            ),
            MaxValueValidator(
                COOKING_TIME_MAX,
                message=f"Максимум {COOKING_TIME_MAX}",
            ),
        ],
        verbose_name="Время приготовления, мин",
    )
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="IngredientAmount",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        "Tag", related_name="recipes", verbose_name="Теги"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    short_code = models.SlugField(
        max_length=SHORTLINK_CODE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Короткий код",
    )

    class Meta:
        ordering = ("-pub_date", "name")
        indexes = [
            models.Index(fields=("name",), name="recipe_name_idx"),
            models.Index(fields=("-pub_date",), name="recipe_pub_date_idx"),
        ]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_code:
            while True:
                code = get_random_string(SHORTLINK_CODE_LENGTH)
                if not Recipe.objects.filter(short_code=code).exists():
                    self.short_code = code
                    break
        return super().save(*args, **kwargs)


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="ingredient_amounts",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        "Ingredient",
        on_delete=models.CASCADE,
        related_name="ingredient_amounts",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN,
                message=f"Минимум {INGREDIENT_AMOUNT_MIN}",
            ),
            MaxValueValidator(
                INGREDIENT_AMOUNT_MAX,
                message=f"Максимум {INGREDIENT_AMOUNT_MAX}",
            ),
        ],
        verbose_name="Количество",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="uniq_recipe_ingredient",
            ),
        ]
        ordering = ("recipe", "ingredient")
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        return f"{self.ingredient} x {self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="in_favorites",
        verbose_name="Рецепт",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="uniq_favorite_user_recipe"
            )
        ]
        indexes = [models.Index(fields=("user",), name="favorite_user_idx")]
        ordering = ("-created",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="in_carts",
        verbose_name="Рецепт",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="uniq_cart_user_recipe"
            )
        ]
        indexes = [models.Index(fields=("user",), name="cart_user_idx")]
        ordering = ("-created",)
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return f"{self.user} - {self.recipe}"
