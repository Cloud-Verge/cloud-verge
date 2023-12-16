import os

from app.utils.common import Singleton


class AppConfig(metaclass=Singleton):
    def __init__(self):
        self.storage_url = os.getenv("STORAGE_URL")
        self.storage_token = os.getenv("STORAGE_TOKEN")
        self.sql_engine_url = os.getenv("SQL_ENGINE_URL")
