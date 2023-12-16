import os

from app.utils.common import Singleton


class AppConfig(metaclass=Singleton):
    def __init__(self):
        self.local_folder = os.getenv("LOCAL_FOLDER")
        self.balancer_url = os.getenv("BALANCER_URL")
        self.balancer_token = os.getenv("BALANCER_TOKEN")
        self.admin_token = os.getenv("ADMIN_TOKEN")
        self.sql_engine_url = os.getenv("SQL_ENGINE_URL")
        self.chunk_size = int(os.getenv("CHUNK_SIZE"))
        self.location = os.getenv("STORAGE_URL")
