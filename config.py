from datetime import timedelta
import os

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASEDIR, 'instance', 'helpdesk.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.replace(chr(92), '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'helpdesk-orchard-secret-2024')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
