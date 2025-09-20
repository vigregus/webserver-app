# Тестовый Web Service на Python

Простой веб-сервис на Python с использованием FastAPI для тестирования и демонстрации.

## Возможности

- ✅ REST API с полным CRUD для пользователей
- ✅ Автоматическая документация (Swagger UI)
- ✅ Проверка состояния сервиса (health check)
- ✅ CORS поддержка
- ✅ Валидация данных с Pydantic
- ✅ Контейнеризация с Docker

## API Эндпоинты

### Основные
- `GET /` - Главная страница
- `GET /health` - Проверка состояния сервиса
- `GET /docs` - Интерактивная документация API
- `GET /stats` - Статистика сервиса

### Пользователи
- `GET /users` - Получить всех пользователей
- `GET /users/{id}` - Получить пользователя по ID
- `POST /users` - Создать нового пользователя
- `PUT /users/{id}` - Обновить пользователя
- `DELETE /users/{id}` - Удалить пользователя

## Установка и запуск

### Локальный запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python main.py
```

Сервер будет доступен по адресу: http://localhost:8000

### Запуск с Docker

1. Соберите образ:
```bash
docker build -t test-webservice .
```

2. Запустите контейнер:
```bash
docker run -p 8000:8000 test-webservice
```

### Запуск с переменными окружения

```bash
PORT=8080 python main.py
```

## Примеры использования

### Создание пользователя
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Иван Иванов",
       "email": "ivan@example.com",
       "age": 30
     }'
```

### Получение всех пользователей
```bash
curl -X GET "http://localhost:8000/users"
```

### Проверка состояния
```bash
curl -X GET "http://localhost:8000/health"
```

## Структура проекта

```
app/
├── main.py              # Основной файл приложения
├── requirements.txt     # Зависимости Python
├── Dockerfile          # Конфигурация Docker
├── .gitignore          # Игнорируемые файлы
└── README.md           # Документация
```

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер
- **Docker** - контейнеризация

## Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python main.py
```
