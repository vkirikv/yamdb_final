# yamdb_final
Проект YaMDb собирает отзывы пользователей на произведения.  

### Стэк технологий:
python 3.7  
django 2.2.16  
djangorestframework 3.12.4  
gunicorn 20.0.4  
nginx  
postgres 13  
docker-compose 3.8

### Как запустить проект:

Клонировать репозиторий:

```
git clone git@github.com:vkirikv/yamdb_final.git
```

Перейти в папку yamdb_final/infra и запустить docker-compose:

```
docker-compose up
```

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input 
```

### Регистрация и авторизация

POST:

http://<your_ip>//api/v1/auth/signup/

Регистрация:


```
{
"email": "string",
"username": "string"
}
```
####Удачная регистрация:

```

{
"email": "string",
"username": "string"
}
```

####Авторизация:

После регистрации на ваш email придет письмо с кодом подтверждения.  
Для авторизации необходимо отправить имя пользователя с кодом подтверждения.

```
{
"username": "string",
"confirmation_code": "string"
}
```

####Удачная авторизация:

```
{
"token": "string"
}
```

### Примеры запросов

#### Пример GET-запроса для получения списка всех произведений
GET http://<your_ip>/api/v1/titles/

Пример ответа *200*:
```
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "name": "string",
        "year": 0,
        "rating": 0,
        "description": "string",
        "genre": [
          {
            "name": "string",
            "slug": "string"
          }
        ],
        "category": {
          "name": "string",
          "slug": "string"
        }
      }
    ]
  }
]
```

#### Пример POST-запроса для добавления нового произведения
POST http://<your_ip>/api/v1/titles/
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
Пример ответа *201*:
```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "string"
    }
  ],
  "category": {
    "name": "string",
    "slug": "string"
  }
}
```
Пример ответа *400*:
```
{
  "field_name": [
    "string"
  ]
}
```

#### Полный перечень примеров
Полный перечень примеров данного проекта можно получить запустив проект и перейдя по [этой ссылке](http://<your_ip>>/redoc/).

### Авторы проекта:
Владимир Кириллов  
Анатолий Баскаков  
Максим Рогушкин

![yamdb_workflow](https://github.com/vkirikv/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)