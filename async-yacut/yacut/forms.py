import json
import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Regexp,
    URL,
)

from .constants import (
    CUSTOM_ID_LENGTH,
    MAX_ORIGINAL_URL_LENGTH,
    SHORT_ID_PATTERN,
)

DEFAULT_SAFE_FILE_EXTS = [
    'png', 'jpg', 'jpeg', 'gif', 'webp',
    'pdf', 'txt', 'csv', 'docx', 'xlsx',
    'pptx', 'zip', 'rar',
]
SAFE_FILE_EXTS = set(json.loads(
    os.getenv('SAFE_FILE_EXTS', json.dumps(DEFAULT_SAFE_FILE_EXTS))
))


class ShortLinkToLinkForm(FlaskForm):
    """Форма для главной страницы"""
    original_link = StringField(
        'Оригинальная длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL'),
            Length(max=MAX_ORIGINAL_URL_LENGTH)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткого идентификатора',
        validators=[
            Optional(),
            Length(max=CUSTOM_ID_LENGTH),
            Regexp(
                SHORT_ID_PATTERN,
                message='Только латиница и цифры',
            )
        ]
    )
    submit = SubmitField('Сгенерировать')


class ShortLinkToFileForm(FlaskForm):
    """Форма для страницы загрузки файлов."""
    files = MultipleFileField(
        "Поле для загрузки файлов",
        validators=[
            FileAllowed(
                SAFE_FILE_EXTS,
                message=(
                    'Недопустимое разрешение файла.'
                    f'Список допустимых разрешений: {SAFE_FILE_EXTS}'
                )
            ),
            DataRequired(
                message='Обязательное поле!'
            )
        ]
    )
    submit = SubmitField('Сгенерировать')
