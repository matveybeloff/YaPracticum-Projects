from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    NumberFilter,
)


class IngredientFilter(FilterSet):
    name = CharFilter(method="filter_name")

    def filter_name(self, qs, name, value):
        if not value:
            return qs
        return qs.filter(name__istartswith=value)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    author = NumberFilter(field_name="author_id")
    is_favorited = BooleanFilter(method="filter_favorited")
    is_in_shopping_cart = BooleanFilter(method="filter_in_cart")

    def filter_favorited(self, qs, name, value):
        user = getattr(self.request, "user", None)
        if value and user and user.is_authenticated:
            return qs.filter(in_favorites__user=user)
        return qs

    def filter_in_cart(self, qs, name, value):
        user = getattr(self.request, "user", None)
        if value and user and user.is_authenticated:
            return qs.filter(in_carts__user=user)
        return qs
