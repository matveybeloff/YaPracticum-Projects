import random
from datetime import datetime

from flask import url_for

from .constants import (
    CUSTOM_ID_LENGTH,
    DEFAULT_SHORT_ID_LENGTH,
    MAX_ORIGINAL_URL_LENGTH,
    RESERVED_SHORT_IDS,
    SYMBOLS,
)
from .error_handler import ShortIDConflictError
from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(MAX_ORIGINAL_URL_LENGTH),
        unique=True,
    )
    short = db.Column(
        db.String(CUSTOM_ID_LENGTH),
        unique=True,
        index=True,
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_file = db.Column(db.Boolean, default=False)

    def to_dict(self, include_short_link=True):
        data = {'url': self.original}
        if include_short_link:
            data['short_link'] = url_for(
                'redirect_view',
                short=self.short,
                _external=True,
            )
        return data

    @staticmethod
    def generate_short_id(length=DEFAULT_SHORT_ID_LENGTH):
        """Генерирует свободный короткий идентификатор."""
        short = ''.join(random.choices(SYMBOLS, k=length))
        while URLMap.is_short_taken(short):
            short = ''.join(random.choices(SYMBOLS, k=length))
        return short

    @staticmethod
    def is_short_taken(short_code):
        """Проверяет, занято ли указанное короткое имя."""
        return (
            short_code in RESERVED_SHORT_IDS
            or URLMap.get_by_short(short_code) is not None
        )

    @staticmethod
    def create_short_link(original, custom_id=None, is_file=False):
        """Создает запись короткой ссылки с учетом резервов и конфликтов."""
        custom_id = (custom_id or '').strip() or None
        if custom_id:
            if URLMap.is_short_taken(custom_id):
                raise ShortIDConflictError(ShortIDConflictError.message)
            short = custom_id
        else:
            short = URLMap.generate_short_id()
        url_map = URLMap(original=original, short=short, is_file=is_file)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_by_short(short_code):
        """Возвращает объект короткой ссылки по идентификатору."""
        return URLMap.query.filter_by(short=short_code).first()
