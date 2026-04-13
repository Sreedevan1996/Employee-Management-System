import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    """
    Base configuration shared across all environments.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-WTF / CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Session / cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # Upload / request size safeguard
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # App behavior
    DEBUG = False
    TESTING = False

    @staticmethod
    def init_app(app):
        """
        Hook for environment-specific initialization.
        """
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """
    Local development configuration.
    Uses SQLite by default.
    """

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'app.db'}"
    )

    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    """
    Configuration for pytest / automated tests.
    """

    TESTING = True
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )

    WTF_CSRF_ENABLED = False

    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    """
    Production configuration.
    Prefer PostgreSQL via DATABASE_URL.
    Falls back to SQLite only if DATABASE_URL is missing.
    """

    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'app.db'}"
    )

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}