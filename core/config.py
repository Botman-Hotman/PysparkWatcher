import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load the stored environment variables
load_dotenv()


class Settings(BaseSettings):
    debug_logs: bool = bool(os.environ.get('debug_logs'))
    dev: bool = bool(os.environ.get('dev'))
    init_db: bool = bool(os.environ.get('init_db'))
    db_string: str = str(os.environ.get('db_string'))
    db_string_async: str = str(os.environ.get('db_string_async'))
    echo_sql: bool = True
    test: bool = False
    staging_schema: str = str(os.environ.get('staging_schema'))
    dw_schema: str = str(os.environ.get('dw_schema'))


class SparkSettings(BaseSettings):
    app_name: str = str(os.environ.get('app_name'))
    master: str = str(os.environ.get('master'))
    spark_log_level: str = str(os.environ.get('spark_log_level'))
    jdbc_url: str = f"{os.environ.get('jdbc_database')}{os.environ.get('db_url')}/{os.environ.get('db_name')}"
    connection_properties: dict = {
        "user":  str(os.environ.get('db_user')),
        "password": str(os.environ.get('db_password')),
        "driver": str(os.environ.get('driver_type'))
    }


settings = Settings()
spark_settings = SparkSettings()
