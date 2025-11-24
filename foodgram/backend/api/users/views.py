from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription, User
from .serializers import (
    SetAvatarSerializer,
    SubscriptionWriteSerializer,
    UserWithRecipesSerializer,
)


class UserViewSet(DjoserUserViewSet):
    @action(
        detail=False,
        methods=["put"],
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        serializer = SetAvatarSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def remove_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        qs = User.objects.filter(
            subscribers__user=request.user
        ).order_by("id")
        page = self.paginate_queryset(qs)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionWriteSerializer(
            data={"author": author.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Подписки не существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)
