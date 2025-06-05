#!/bin/bash
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate --noinput

# Сбор статических файлов
python manage.py collectstatic --noinput

# Создание суперпользователя (если необходимо)
python manage.py createsuperuser --noinput || true
