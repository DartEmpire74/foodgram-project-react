[![Actions Status](https://github.com/DartEmpire74/foodgram-project-react/workflows/main.yml/badge.svg)](https://github.com/DartEmpire74/foodgram-project-react/actions)

# Foodgram - вкусные рецепты 
## `https://foodgram.3utilities.com`
Наш проект это сайт, на котором пользователи будут публиковать рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Пользователям сайта также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Стек технологий 
## Backend
- Django
- PostgreSQL
- Django REST Framework

## Frontend
- React

## Gateway
- Nginx
- Certbot

# Развертывание проекта

Для развертывания проекта вам потребуется установить Docker и Docker Compose, 
если они еще не установлены на вашем сервере.

## Шаги развертывания
1. Скопируйте файл `docker-compose.yml` в корневую директорию вашего проекта.
2. Создайте файл .env и укажите в нем следующую информацию: 
`ALLOWED_HOSTS, DEBUG, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DB_NAME, DB_HOST, DB_PORT`.

### Пример файла .env: 
```
ALLOWED_HOSTS= 127.0.0.1,localhost
DEBUG=true

POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
DB_NAME=your_database

DB_HOST = db
DB_PORT = 5432
```

3. В командной строке перейдите в директорию с вашим проектом.
4. Запустите контейнеры с помощью команды:
```
docker-compose docker compose up -d
```
5. Создайте суперпользователя для доступа в admin сайта.
6. После успешного запуска всех контейнеров ваше приложение будет доступно по адресу 
`http://ваш_домен`.

## Миграции данных

### Добавление тегов
Чтобы добавить предустановленные теги в базу данных, выполните миграцию, 
которая включает скрипт для добавления тегов.

Пример файла миграции для добавления тегов:
```
# migrations/0004_add_tags.py

from django.db import migrations
from recipes.utils import random_color

def add_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    tags = [
        ('веганский', 'vegan', random_color()),
        ('безглютеновый', 'gluten_free', random_color()),
        ('низкокалорийный', 'low_calorie', random_color()),
        # Добавьте дополнительные теги по желанию
    ]
    for name, slug, color in tags:
        Tag.objects.get_or_create(name=name, slug=slug, defaults={'color': color})

class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0003_previous_migration'),  # замените на актуальное имя миграции
    ]

    operations = [
        migrations.RunPython(add_tags),
    ]
```
Запустите миграции с помощью команды:
```
python manage.py migrate
```

### Добавление ингредиентов
Чтобы добавить ингредиенты в базу данных, вам следует выполнить миграцию, которая будет включать скрипт 
для их добавления. Это обеспечит автоматическую инициализацию данных при первом развертывании проекта.

Пример файла миграции для добавления ингредиентов:
```
# migrations/0005_add_ingredients.py

import csv
from django.db import migrations

def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    with open('path_to_ingredients_csv_file.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            name, measurement_unit = row
            Ingredient.objects.get_or_create(name=name, defaults={'measurement_unit': measurement_unit})

class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0004_add_tags'),  # Убедитесь, что это актуальная зависимость
    ]

    operations = [
        migrations.RunPython(add_ingredients),
    ]
```

Перед выполнением миграции убедитесь, что файл CSV с данными о ингредиентах находится в указанном месте и 
содержит нужные данные.
Запустите миграции с помощью команды:
```
python manage.py migrate
```

[Документация к API](https://foodgram.3utilities.com/api/docs/)