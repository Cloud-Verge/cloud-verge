import os

from app.utils.common import Singleton


class AppConfig(metaclass=Singleton):
    def __init__(self):
        self.local_folder = os.getenv("LOCAL_FOLDER")
        self.admin_token = os.getenv("ADMIN_TOKEN")
        self.sql_engine_url = os.getenv("SQL_ENGINE_URL")
        self.chunk_size = int(os.getenv("CHUNK_SIZE"))
