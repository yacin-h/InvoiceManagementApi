from sqlmodel import create_engine
from sqlalchemy import URL
from dotenv import load_dotenv, find_dotenv
from os import getenv


path = find_dotenv()
if not load_dotenv(path):
    raise RuntimeError("Failed to load environment variables from .env file")

DB_DRIVER = getenv("DB_DRIVER", "sqlite")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT", "5432")
DB_NAME = getenv("DB_NAME", "mydatabase")
DB_USER = getenv("DB_USERNAME", "user")
DB_PASSWORD = getenv("DB_PASSWORD", "password")


def get_url():
    if DB_DRIVER == "sqlite":
        return f"sqlite:///./{DB_NAME}.db"
    else:
        return URL().create(
            DB_DRIVER,
            database=DB_NAME,
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )


def get_engine():

    _url = get_url()

    if "sqlite" in _url:
        _connect_args = {"check_same_thread": False}
        return create_engine(_url, connect_args=_connect_args)
    else:
        return create_engine(_url)


engine = get_engine()
