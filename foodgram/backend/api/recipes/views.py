from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeListSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    FavoriteWriteSerializer,
    ShoppingCartWriteSerializer,
)
from .filters import IngredientFilter, RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects.select_related("author")
            .prefetch_related(
                "tags",
                Prefetch(
                    "ingredient_amounts",
                    queryset=IngredientAmount.objects.select_related(
                        "ingredient"
                    ),
                ),
            )
            .order_by("-pub_date")
        )

    def get_serializer_class(self):
        return (
            RecipeWriteSerializer
            if self.request.method not in {"GET", "HEAD"}
            else RecipeListSerializer
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        url_path="get-link",
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        return Response(
            {
                "short-link": request.build_absolute_uri(
                    f"/s/{recipe.short_code}"
                )
            }
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        serializer = FavoriteWriteSerializer(
            data={"recipe": recipe.pk}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        recipe = self.get_object()
        deleted, _ = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Рецепта нет в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        serializer = ShoppingCartWriteSerializer(
            data={"recipe": recipe.pk}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        deleted, _ = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Рецепта нет в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        qs = (
            IngredientAmount.objects.filter(
                recipe__in_carts__user=request.user
            )
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(total=Sum("amount"))
            .order_by("name")
        )
        lines = [
            f"{row['name']} ({row['unit']}) - {row['total']}" for row in qs
        ]
        content = "Список покупок:\n" + "\n".join(lines) + "\n"
        resp = HttpResponse(content, content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = (
            "attachment; filename=\"shopping_list.txt\""
        )
        return resp


class ShortLinkRedirectView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        recipe = get_object_or_404(Recipe, short_code=code)
        return redirect(f"/recipes/{recipe.id}/")
