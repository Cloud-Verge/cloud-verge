import os


class AppConfig:
    GRPC_PORT = os.getenv("GRPC_PORT")
    SQL_ENGINE_URI = os.getenv("SQL_ENGINE_URI")
