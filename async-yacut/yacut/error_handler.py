from http import HTTPStatus

from flask import jsonify

from . import app


class APIError(Exception):
    status_code = HTTPStatus.BAD_REQUEST
    message = ''

    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}


class InvalidShortIDError(APIError):
    message = 'Указано недопустимое имя для короткой ссылки'


class ShortIDConflictError(APIError):
    message = 'Предложенный вариант короткой ссылки уже существует.'


@app.errorhandler(APIError)
def handle_api_error(error):
    """Возвращает JSON-ответ для ошибок API."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def handle_not_found(_error):
    """Возвращает JSON-ответ для 404."""
    return jsonify({'message': 'Страница не найдена'}), HTTPStatus.NOT_FOUND
