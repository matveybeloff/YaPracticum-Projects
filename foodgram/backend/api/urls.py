from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions as drf_permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Foodgram API",
        default_version="v1",
        description="Документация API Foodgram",
    ),
    public=True,
    permission_classes=(drf_permissions.AllowAny,),
)


urlpatterns = [
    path("", include("api.users.urls")),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),

    path("", include("api.recipes.urls")),

    path(
        "docs/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="api-docs",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="api-swagger",
    ),
    path(
        "schema.json",
        schema_view.without_ui(cache_timeout=0),
        name="api-schema-json",
    ),
]
