from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from pydantic import BaseModel

app = FastAPI(
    title="Test API", description="Тестовое API для демонстрации", version="0.1.2"
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для Docker
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class User(BaseModel):
    id: int | None = None
    name: str
    email: str
    age: int


class UserCreate(BaseModel):
    name: str
    email: str
    age: int


# Временное хранилище данных
users_db: list[dict[str, Any]] = []
user_id_counter: int = 1

# Prometheus metrics
METRIC_USERS_TOTAL = Gauge("app_users_total", "Total users count in memory store")
METRIC_REQUESTS_TOTAL = Counter(
    "app_requests_total", "Total API requests", ["endpoint", "method"]
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/", method="GET").inc()
    return {"message": "Добро пожаловать в тестовое API!"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/health", method="GET").inc()
    return {"status": "healthy", "service": "backend-api"}


@app.get("/api/config")
async def get_config():
    """Получить конфигурацию для frontend"""
    return {"apiUrl": "http://localhost:8000", "version": "1.0.0"}


@app.get("/api/users", response_model=list[User])
async def get_users():
    """Получить всех пользователей"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/api/users", method="GET").inc()
    return users_db


@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/api/users/{user_id}", method="GET").inc()
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate):
    """Создать нового пользователя"""
    global user_id_counter
    METRIC_REQUESTS_TOTAL.labels(endpoint="/api/users", method="POST").inc()

    # Проверка на существующий email
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        )

    new_user = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email,
        "age": user.age,
    }

    users_db.append(new_user)
    user_id_counter += 1
    METRIC_USERS_TOTAL.set(len(users_db))

    return new_user


@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate):
    """Обновить пользователя"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/api/users/{user_id}", method="PUT").inc()
    user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка на существующий email (кроме текущего пользователя)
    if any(u["email"] == user.email and u["id"] != user_id for u in users_db):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        )

    users_db[user_index] = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
    }

    return users_db[user_index]


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    """Удалить пользователя"""
    METRIC_REQUESTS_TOTAL.labels(endpoint="/api/users/{user_id}", method="DELETE").inc()
    user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    deleted_user = users_db.pop(user_index)
    METRIC_USERS_TOTAL.set(len(users_db))
    return {"message": f"Пользователь {deleted_user['name']} удален"}


@app.get("/metrics")
async def metrics() -> Response:
    """Эндпоинт Prometheus metrics"""
    METRIC_USERS_TOTAL.set(len(users_db))
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/stats")
async def get_stats():
    """Получить статистику"""
    total_users = len(users_db)
    avg_age = sum(u["age"] for u in users_db) / total_users if total_users > 0 else 0

    return {
        "total_users": total_users,
        "average_age": round(avg_age, 2),
        "users_by_age_group": {
            "18-25": len([u for u in users_db if 18 <= u["age"] <= 25]),
            "26-35": len([u for u in users_db if 26 <= u["age"] <= 35]),
            "36-50": len([u for u in users_db if 36 <= u["age"] <= 50]),
            "50+": len([u for u in users_db if u["age"] > 50]),
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
