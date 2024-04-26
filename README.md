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
5. После успешного запуска всех контейнеров ваше приложение будет доступно по адресу 
`http://ваш_домен`.
