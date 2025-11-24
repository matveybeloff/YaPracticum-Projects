from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField("Email", unique=True)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    avatar = models.ImageField(
        "Аватар",
        upload_to="users/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator([
                "jpg",
                "jpeg",
                "png",
                "gif",
                "webp",
            ])
        ],
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username", "email")

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_subscribe",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.author}"
