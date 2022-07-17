import json

import aioredis
import src.api.v1.model.api_model as genre
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from src.api.v1.api_films import film_router
from src.api.v1.api_genre import genre_router
from src.api.v1.api_person import person_router
from src.api.v1.auth import auth_router
from src.core.config import Settings
from src.db import elastic, redis
from starlette.middleware.sessions import SessionMiddleware

first_update_genre = True
settings = Settings()

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=settings.project_name,
    # Адрес документации в красивом интерфейсе
    docs_url="/api/openapi",
    # Адрес документации в формате OpenAPI
    openapi_url="/api/openapi.json",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)

# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(film_router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(genre_router, prefix="/api/v1/genres", tags=["Жанры"])
app.include_router(person_router, prefix="/api/v1/person", tags=["Персоны"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Авторизация"])


@app.on_event("startup")
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis.redis = await aioredis.Redis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db_number}"
    )
    elastic.es = AsyncElasticsearch(
        f"http://{settings.elastic_host}:{settings.elastic_port}", api_key="hello world"
    )


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    global first_update_genre
    response = await call_next(request)
    if (request.url.path == "/api/openapi") or first_update_genre:
        genre.GenreEnum = await genre.GenreEnum.update_genre()
        if len(genre.GenreEnum):
            first_update_genre = False
    return response


@app.middleware("http")
async def check_access(request: Request, call_next):
    if request.url.path not in ["/api/openapi", "/api/openapi.json"]:

        headers = {"Authorization": f'Bearer {request.session.get("token") or ""}'}
        cookies = {"refresh_token": request.cookies.get("refresh_token")}
        url = (
            f"http://{settings.auth_host}:{settings.auth_port}/auth/api/v1/check_access"
        )
        data = json.dumps({"path": request.url.path})
        cli = ClientSession(headers=headers, cookies=cookies)
        try:
            response = await cli.post(url=url, data=data)
        except ClientConnectorError:
            # Связь с Auth сервером не установлена
            await cli.close()
            return Response(
                media_type="Application/json",
                content=json.dumps(
                    {"message": "The service is temporarily unavailable"}
                ),
            )
        await cli.close()
        request.session["token"] = response.headers.get("token")
        request.cookies["refresh_token"] = response.cookies.get("refresh_token").value
        if response.status != 200:
            resp = Response(status_code=403)
            resp.headers.append("token", response.headers.get("token"))
            resp.set_cookie(
                "refresh_token", response.cookies.get("refresh_token").value
            )
            return resp
    return await call_next(request)


app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
