import logging

import psycopg2
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from src.core.config import settings
from werkzeug.security import generate_password_hash

db_postgres = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.postgres_dsn
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db_postgres.init_app(app)
    migrate.init_app(app, db_postgres)
    create_partition_user_sign_in()
    return db_postgres


def init_superuser(email: str, password: str):
    from src.db.models.db_models import User

    if (
        not db_postgres.session.query(User)
        .filter(User.super_user is True)
        .update(
            {
                "email": email,
                "password": generate_password_hash(password),
                "super_user": True,
            }
        )
    ):
        db_postgres.session.add(
            User(
                email=settings.auth_login,
                password=generate_password_hash(settings.auth_password),
                super_user=True,
            )
        )
    try:
        db_postgres.session.commit()
    except IntegrityError:
        pass


def init_roles():
    from src.db.models.db_models import Role

    for role in [
        Role(id="97cd9d35-890c-4a2a-8321-08d9b1a83182", name="anonymous"),
        Role(id="97cd9d35-890c-4a2a-8321-08d9b1a83189", name="subscriber"),
    ]:
        try:
            db_postgres.session.add(role)
        except PendingRollbackError:
            pass
        except IntegrityError:
            pass
        db_postgres.session.commit()


def create_partition_user_sign_in():
    """Создание partition user_sign_in, ибо в моделях не понимаю как это сделать,
    так как пример из учебного материала почему-то у меня не работает, он там болтается"""
    text = """   
    CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('pc');
    CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile');
    CREATE TABLE IF NOT EXISTS "user_sign_in_tablet" PARTITION OF "users_sign_in" FOR VALUES IN ('tablet');
    CREATE TABLE IF NOT EXISTS "user_sign_in_other" PARTITION OF "users_sign_in" FOR VALUES IN ('other');"""

    pg_connect = psycopg2.connect(settings.postgres_dsn)
    with pg_connect as conn, conn.cursor() as pg_cursor:
        for sql in text.split(";"):
            try:
                pg_cursor.execute(sql)
                conn.commit()
            except psycopg2.ProgrammingError:
                conn.rollback()
            except psycopg2.IntegrityError:
                conn.rollback()
    logging.info(" create_partition_user_sign_in: OK")

    pg_connect = psycopg2.connect(settings.postgres_dsn)
    with pg_connect as conn, conn.cursor() as pg_cursor:
        for sql in text.split(";"):
            try:
                pg_cursor.execute(sql)
                conn.commit()
            except psycopg2.ProgrammingError:
                conn.rollback()
            except psycopg2.IntegrityError:
                conn.rollback()
    logging.info(" create_partition_user_sign_in: OK")
