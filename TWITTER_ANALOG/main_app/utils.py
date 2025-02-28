import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import current_app
from main_app.models import User, db
import uuid


def create_default_user():
    if not User.query.filter_by(name="default_user").first():
        new_user = User(name="default_user", api_key="test")
        db.session.add(new_user)
        db.session.commit()


def create_additional_user():
    if not User.query.filter_by(name="additional_user").first():
        user_key = str(uuid.uuid4())
        new_user = User(name="additional_user", api_key=user_key)
        db.session.add(new_user)
        db.session.commit()


def create_db_if_not_exist():
    user = current_app.config["POSTGRES_USER"]
    password = current_app.config["POSTGRES_PASSWORD"]
    host = current_app.config["POSTGRES_HOST"]
    port = current_app.config["POSTGRES_PORT"]
    db_name = current_app.config["DATABASE_NAME"]
    conn = psycopg2.connect(
        dbname="postgres", user=user, password=password, host=host, port=port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()
    conn.close()
