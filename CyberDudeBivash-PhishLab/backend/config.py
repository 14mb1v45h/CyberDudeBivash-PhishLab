# backend/config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cdb-dev-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "phishlab.db")

    # 🔐 Simple admin credentials (override via env in real use)
    ADMIN_USERNAME = os.environ.get("CDB_ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.environ.get("CDB_ADMIN_PASS", "changeme")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


config = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig
}
