Импорт ингредиентов из CSV (management-команда)

Команда загружает справочник ингредиентов в модель recipes.Ingredient из CSV-файла.

По умолчанию команда ищет файл `foodgram/data/ingredients.csv`.

Запуск:

```
python manage.py import_csv
```

Можно:

- Явно указать CSV-файл:

```
python manage.py import_csv --file path/to/ingredients.csv
```

- Очистить таблицу перед импортом:

```
python manage.py import_csv --truncate
```

- Кодировка файла (по умолчанию команда пробует cp1251, затем utf-8-sig):

```
python manage.py import_csv --encoding cp1251
python manage.py import_csv --encoding utf-8-sig
```

Лог работы команды:

```
foodgram/backend/recipes/management/commands/import_csv.log
```

Требования:

- Наличие миграций (`python manage.py migrate`).
- В CSV должны быть столбцы `name` и `measurement_unit` (допустимы альтернативные заголовки `unit`/`measure`).

