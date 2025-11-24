# Foodgram

Кулинарный сервис: пользователи публикуют рецепты, подписываются на авторов, добавляют рецепты в «Избранное» и «Список покупок», скачивают список ингредиентов. Полный REST API, фронтенд, документация.

## Что внутри
- Backend: Django + DRF, токены (authtoken), django-filter, Djoser, drf-yasg
- DB: PostgreSQL
- Frontend: React (собран в образ и отдается через Nginx)
- Прод: Docker + docker-compose, Gunicorn, Nginx

## Быстрый старт в Docker (прод-сборка)
1) Клонируйте репозиторий и перейдите в каталог `foodgram`.
2) Создайте `.env` на основе `.env.example` и укажите:
   - `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - `DB_HOST=db`, `DB_PORT=5432`
   - `STATIC_ROOT=/static`, `MEDIA_ROOT=/media`
   - `DOCKER_USERNAME=<ваш_dockerhub_аккаунт>` (compose использует `${DOCKER_USERNAME}/foodgram_*:latest`)
3) Запустите:
```
docker compose -f docker-compose.production.yml up -d
```
4) Приложение будет доступно: `http://localhost:9000/` (Nginx gateway).

Примечания
- Контейнер `db` стартует первым, backend ждёт готовности БД.
- Статика фронтенда автоматически копируется в общий volume `static`.
- Медиа-файлы пишутся в volume `media`.

## Локальный запуск backend (без Docker)
```
cd foodgram/backend
python -m venv venv && venv/Scripts/activate  # Windows; macOS/Linux: source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

## Наполнение БД данными
- Базовые теги и ингредиенты подгружаются автоматически миграцией при первом `migrate` (из `foodgram/data/ingredients.json`).
- Дополнительно (по желанию):
```
cd foodgram/backend
python manage.py load_tags                  # создать/обновить дефолтные теги
python manage.py import_csv --file ../data/ingredients.csv  # импортировать ингредиенты из CSV
```

## Документация API
- ReDoc: `http://localhost:9000/api/docs/` (или `http://127.0.0.1:8000/api/docs/` при локальном запуске)
- Swagger UI: `http://localhost:9000/api/swagger/`
- JSON-схема: `http://localhost:9000/api/schema.json`

## Примеры запросов

- Регистрация пользователя
```
POST /api/users/
{
  "email": "user@example.com",
  "username": "user",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "password": "secret"
}

201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "first_name": "Имя",
  "last_name": "Фамилия"
}
```

- Получение токена
```
POST /api/auth/token/login/
{
  "email": "user@example.com",
  "password": "secret"
}

200 OK
{ "auth_token": "xxxxxxxx" }
```

- Создание рецепта (картинка — data URI)
```
POST /api/recipes/  (Authorization: Token <auth_token>)
{
  "ingredients": [ {"id": 1, "amount": 2} ],
  "tags": [1],
  "image": "data:image/png;base64,iVBORw0KGgo...",
  "name": "Омлет",
  "text": "Взбить яйца и обжарить",
  "cooking_time": 5
}

201 Created
{ "id": 1, "name": "Омлет", ... }
```

- Теги и ингредиенты
```
GET /api/tags/
200 OK  [ {"id": 1, "name": "Завтрак", "slug": "breakfast"}, ... ]

GET /api/ingredients/?name=мо
200 OK  [ {"id": 1, "name": "Молоко", "measurement_unit": "мл"}, ... ]
```

## Автор
- Имя: Матвей Белов
- Email: matveybeloff@mail.ru
- GitHub: https://github.com/matveybeloff
