![Foodgram Workflow](https://github.com/DartEmpire74/foodgram-project-react/actions/workflows/main.yml/badge.svg)

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
6. В проекте реализованы миграции данных. В миграции зашито автоматическое наполение тегов и ингредиентов.
При необходимости, вы можете отключить автонаполнение при помощи настроек в settings.py проекта:
```
ENABLE_INGREDIENT_MIGRATIONS = True

ENABLE_TAG_MIGRATIONS = True
```
### Добавление ингредиентов: 
Пример файла с данными о ингредиентах находится в директории backend/ingredient_data. Вы также можете создать 
свой собственный перечень ингредиентов и заменить старый файл своим. Перед выполнением миграции убедитесь, что файл CSV с данными о ингредиентах находится в указанном месте и 
содержит нужные данные.

### Добавление тегов
Чтобы добавить предустановленные теги в базу данных, выполните миграцию, 
которая включает скрипт для добавления тегов. При необходимости вы можете изменить теги на собственные. 
Для этого вам необходимо внести изменения в файл миграций. 

Вот так выглядит код добавления тегов: 
```
... 
# recipes/migrations/0003_add_tags.py

def add_tags(apps, schema_editor):
    if not settings.ENABLE_TAG_MIGRATIONS:
        return
    Tag = apps.get_model('recipes', 'Tag')
    tags = [
       # Название тега, slug, цвет тега (по умолчанию задается рандомно) 
        ('веганский', 'vegan', random_color()),
        ('безглютеновый', 'gluten_free', random_color()),
        ('низкокалорийный', 'low_calorie', random_color()),
    ]
    for name, slug, color in tags:
        Tag.objects.get_or_create(name=name, slug=slug, defaults={'color': color})

...
```
7. После этого примените миграции с помощью команды: 
```
docker compose exec backend python manage.py migrate
```
8. Соберите статику backend при помощи команд. 
```
compose exec backend python manage.py collectstatic
compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
9. После успешного запуска всех контейнеров ваше приложение будет доступно по адресу 
`http://ваш_домен`.

[Документация к API](https://foodgram.3utilities.com/api/docs/)