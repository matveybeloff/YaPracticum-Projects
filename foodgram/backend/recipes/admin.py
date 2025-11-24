from django.contrib import admin
from django.db.models import Count

from .models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "pub_date",
        "favorites_count",
    )
    list_filter = ("author", "tags")
    search_fields = ("name", "author__username", "author__email")
    inlines = (IngredientAmountInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_fav_count=Count("in_favorites"))

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return getattr(obj, "_fav_count", None) or obj.in_favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name", "slug")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
