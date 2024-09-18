import argparse
import asyncio

from core.config import settings, spark_settings
from logging.handlers import RotatingFileHandler
from core.db import async_session_factory, async_engine, drop_all_schema, create_all_schema
from services.directory_watcher import watch_folder
import logging

from services.schema_init import SchemaInit, populate_dimensions_on_startup

logging.basicConfig(
    format='%(asctime)s : %(name)s :  %(levelname)s : %(funcName)s :  %(message)s'
    , level=logging.DEBUG if settings.debug_logs else logging.INFO
    , handlers=[
        RotatingFileHandler(
            filename=f"logs/{spark_settings.app_name}.log",
            maxBytes=10 * 1024 * 1024,  # 100 MB per file,
            backupCount=7  # keep 7 backups
        ),
        logging.StreamHandler()  # Continue to log to the console as well
    ]
)

# Create arg parser object
parser = argparse.ArgumentParser()
parser.add_argument("--watch", help="start the file watching system on a specified folder i.e. --watch 'imports'")


async def init_database():
    if settings.init_db:
        logging.info("Starting database initialisation.")
        async with async_session_factory() as session:
            logging.info(f"Creating schema for {settings.dw_schema}.")
            await SchemaInit().create_schema(session, settings.dw_schema)

        if settings.dev:
            logging.info("Dropping all schemas for dev environment.")
            await drop_all_schema()  # drop the schema for dev work
        logging.info("Creating all schemas.")
        await create_all_schema()

        async with async_session_factory() as session:
            logging.info("Populating dimensions on startup.")
            await populate_dimensions_on_startup(session)


async def watcher(target_directory):
    await init_database()

    loop = asyncio.get_running_loop()
    await watch_folder(loop, target_directory)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.watch:
        # Run the main function asynchronously
        asyncio.run(watcher(args.watch))