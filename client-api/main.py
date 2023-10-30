from app.app import create_app
from app.config import AppCofig

app = create_app(AppCofig('config.yml'))
