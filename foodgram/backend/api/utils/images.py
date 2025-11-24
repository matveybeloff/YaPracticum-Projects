import base64
import binascii
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


def decode_data_uri_image(
    value: str,
    prefix: str = "",
    allowed_mime: dict | None = None,
):
    if not isinstance(value, str) or not value.startswith("data:"):
        raise serializers.ValidationError(
            {"image": ["Неверный формат изображения: ожидается data URI."]}
        )

    try:
        header, b64data = value.split(",", 1)
    except ValueError:
        raise serializers.ValidationError(
            {"image": ["Некорректный data URI (заголовок)."]}
        )

    if ";base64" not in header:
        raise serializers.ValidationError(
            {"image": ["Некорректный data URI (ожидается base64)."]}
        )

    mime = header[5:].split(";", 1)[0]
    if allowed_mime is None:
        raise serializers.ValidationError(
            {"image": ["Разрешённые MIME-типы не заданы."]}
        )
    ext = allowed_mime.get(mime)
    if not ext:
        raise serializers.ValidationError(
            {"image": ["Недопустимый MIME-тип изображения."]}
        )

    try:
        raw = base64.b64decode(b64data, validate=True)
    except (binascii.Error, ValueError):
        raise serializers.ValidationError(
            {"image": ["Ошибка декодирования base64."]}
        )

    filename = f"{prefix}{uuid.uuid4().hex}.{ext}"
    return ContentFile(raw, name=filename)
