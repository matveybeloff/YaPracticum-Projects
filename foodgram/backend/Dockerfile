FROM python:3.11

WORKDIR /app

RUN pip install --no-cache-dir gunicorn==21.2.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Рабочая директория с manage.py и модулем config
WORKDIR /app/backend

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]
