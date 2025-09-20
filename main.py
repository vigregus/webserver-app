"""
Тестовый веб-сервис на Python с FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import os
from datetime import datetime

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Тестовый Web Service",
    description="Простой веб-сервис для тестирования",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: str


# Временное хранилище данных (в реальном приложении используется БД)
users_db: List[Dict] = []
user_counter = 1


@app.get("/", response_model=Dict[str, str])
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в тестовый веб-сервис!",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    return HealthResponse(
        status="healthy", timestamp=datetime.now().isoformat(), version="1.0.0"
    )


@app.get("/users", response_model=List[UserResponse])
async def get_users():
    """Получить всех пользователей"""
    return [
        UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            age=user.get("age"),
            created_at=user["created_at"],
        )
        for user in users_db
    ]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        age=user.get("age"),
        created_at=user["created_at"],
    )


@app.post("/users", response_model=UserResponse)
async def create_user(user: User):
    """Создать нового пользователя"""
    global user_counter

    new_user = {
        "id": user_counter,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "created_at": datetime.now().isoformat(),
    }

    users_db.append(new_user)
    user_counter += 1

    return UserResponse(
        id=new_user["id"],
        name=new_user["name"],
        email=new_user["email"],
        age=new_user["age"],
        created_at=new_user["created_at"],
    )


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: User):
    """Обновить пользователя"""
    user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    users_db[user_index].update(
        {"name": user.name, "email": user.email, "age": user.age}
    )

    updated_user = users_db[user_index]
    return UserResponse(
        id=updated_user["id"],
        name=updated_user["name"],
        email=updated_user["email"],
        age=updated_user["age"],
        created_at=updated_user["created_at"],
    )


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Удалить пользователя"""
    user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    deleted_user = users_db.pop(user_index)
    return {"message": f"Пользователь {deleted_user['name']} удален"}


@app.get("/stats")
async def get_stats():
    """Получить статистику сервиса"""
    return {
        "total_users": len(users_db),
        "service_uptime": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


if __name__ == "__main__":
    # Запуск сервера
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
