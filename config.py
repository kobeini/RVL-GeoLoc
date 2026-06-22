import os

from dotenv import load_dotenv

load_dotenv()


def _mysql_uri() -> str:
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    name = os.environ.get("MYSQL_DATABASE", "rvlgeoloc")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


def _postgis_uri() -> str:
    user = os.environ.get("POSTGIS_USER", "postgres")
    password = os.environ.get("POSTGIS_PASSWORD", "")
    host = os.environ.get("POSTGIS_HOST", "localhost")
    port = os.environ.get("POSTGIS_PORT", "5432")
    name = os.environ.get("POSTGIS_DATABASE", "rvlgeoloc")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "nainha")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("MYSQL_DATABASE_URL", _mysql_uri())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    POSTGIS_DATABASE_URI = os.environ.get("POSTGIS_DATABASE_URL", _postgis_uri())


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

    def __init__(self):
        if Config.SECRET_KEY == "nainha":
            raise RuntimeError(
                "SECRET_KEY must be set via environment variable in production."
            )


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
