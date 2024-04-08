import os

from utils.common import Singleton


class AppConfig(metaclass=Singleton):
    STORAGE_URL = os.getenv("STORAGE_URL")
    STORAGE_TOKEN = os.getenv("STORAGE_TOKEN")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    SQL_ENGINE_URI = os.getenv("SQL_ENGINE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
