from fastapi import FastAPI, Path, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="FastAPI Metanit + CRUD Users",
    description="Примеры из первых 5 статей Metanit и CRUD-операции для пользователей",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # настройка Swagger UI
)

@app.get("/", response_class=HTMLResponse, tags=["Примеры Metanit"])
def read_root():
    return HTMLResponse(content="<h2>Hello METANIT.COM!</h2>")

@app.get("/hello", tags=["Примеры Metanit"])
def hello():
    return {"message": "Hello METANIT.COM"}


@app.get("/text", response_class=PlainTextResponse, tags=["Примеры Metanit"])
def plain_text():
    return "Hello METANIT.COM"


@app.get("/custom-response", tags=["Примеры Metanit"])
def custom_response():
    return JSONResponse(content={"message": "Custom JSONResponse"}, status_code=200)


@app.get("/file", response_class=FileResponse, tags=["Примеры Metanit"])
def send_file():
    return "app/public/index.html"


@app.get("/download", response_class=FileResponse, tags=["Примеры Metanit"])
def download_file():
    return FileResponse(
        "app/public/index.html",
        filename="mainpage.html",
        media_type="application/octet-stream"
    )


@app.get("/users/{user_id}", tags=["Примеры Metanit"])
def get_user_path(user_id: int = Path(..., ge=1, description="ID пользователя")):
    return {"user_id": user_id}


@app.get("/users/{name}-{age}", tags=["Примеры Metanit"])
def get_user_name_age(
    name: str = Path(..., min_length=1, description="Имя"),
    age: int = Path(..., ge=0, le=150, description="Возраст")
):
    return {"user_name": name, "user_age": age}

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Email")
    age: Optional[int] = Field(None, ge=0, le=150, description="Возраст (необязательно)")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: datetime


users_db: dict[int, dict] = {}
_next_id: int = 1


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["CRUD Users"],
    summary="Создать пользователя",
    description="Создаёт нового пользователя и возвращает его данные с присвоенным ID."
)
def create_user(user: UserCreate):
    global _next_id
    user_id = _next_id
    _next_id += 1

    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = user_data
    return user_data


@app.get(
    "/api/users",
    response_model=list[UserResponse],
    tags=["CRUD Users"],
    summary="Получить список пользователей"
)
def list_users(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей")
):
    all_users = list(users_db.values())
    return all_users[skip: skip + limit]


@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["CRUD Users"],
    summary="Получить пользователя по ID"
)
def get_user(user_id: int = Path(..., ge=1, description="ID пользователя")):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    return users_db[user_id]


@app.put(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["CRUD Users"],
    summary="Обновить пользователя (полностью или частично)"
)
def update_user(
    user_id: int = Path(..., ge=1, description="ID пользователя"),
    user_update: UserUpdate = ...
):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    stored = users_db[user_id]
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        stored[field] = value

    return stored


@app.delete(
    "/api/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["CRUD Users"],
    summary="Удалить пользователя"
)
def delete_user(user_id: int = Path(..., ge=1, description="ID пользователя")):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    del users_db[user_id]
    return None