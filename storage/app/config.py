import os

from app.utils.common import Singleton


class AppConfig(metaclass=Singleton):
    LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
    BALANCER_URL = os.getenv("BALANCER_URL")
    BALANCER_TOKEN = os.getenv("BALANCER_TOKEN")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    SQL_ENGINE_URI = os.getenv("SQL_ENGINE_URI")
    CHUNK_SIZE = os.getenv("CHUNK_SIZE")
