from http import HTTPStatus

from flask import jsonify, request

from . import app
from .constants import SHORT_ID_PATTERN
from .error_handler import APIError, InvalidShortIDError
from .models import URLMap

MISSING_BODY_MSG = 'Отсутствует тело запроса'
MISSING_URL_MSG = '"url" является обязательным полем!'
NOT_FOUND_MSG = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def create_short_id():
    """Создает короткую ссылку через API."""
    data = request.get_json(silent=True)
    if not data:
        raise APIError(
            MISSING_BODY_MSG,
            HTTPStatus.BAD_REQUEST,
        )
    original = data.get('url')
    if not original:
        raise APIError(
            MISSING_URL_MSG,
            HTTPStatus.BAD_REQUEST,
        )
    custom_id = data.get('custom_id')
    if custom_id and not SHORT_ID_PATTERN.match(str(custom_id).strip()):
        raise APIError(
            InvalidShortIDError.message,
            HTTPStatus.BAD_REQUEST,
        )
    url_map = URLMap.create_short_link(
        original=original,
        custom_id=custom_id,
    )
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Возвращает оригинальный URL по короткому идентификатору."""
    url_map = URLMap.get_by_short(short_id)
    if not url_map:
        raise APIError(
            NOT_FOUND_MSG,
            HTTPStatus.NOT_FOUND,
        )
    return jsonify(
        url_map.to_dict(include_short_link=False),
    ), HTTPStatus.OK
