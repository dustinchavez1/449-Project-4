import contextlib
import logging.config
import sqlite3

from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from itertools import cycle

class Settings(BaseSettings, env_file=".env", extra="ignore"):
    users_database: str
    secondary_database: str
    tertiary_database: str
    logging_config: str


settings = Settings()
app = FastAPI()

def get_logger():
    return logging.getLogger(__name__)

# Database URLS which itertools will cycle through
SECONDARY_DB_URLS = [settings.secondary_database, settings.tertiary_database]
secondary_cycle = cycle(SECONDARY_DB_URLS)

def get_db(logger: logging.Logger = Depends(get_logger)):
    def selective_logging (statement):
        if statement.upper().strip().startswith('SELECT'):
            logger.debug(statement)
    with contextlib.closing(sqlite3.connect(settings.users_database)) as db:
        db.row_factory = sqlite3.Row
        db.set_trace_callback(selective_logging)
        yield db

# Use itertools.cycle() to rotate between secondary_database and tertiary_database with secondary_cycle
def get_secondary_db(logger: logging.Logger = Depends(get_logger)):
    url = next(secondary_cycle)
    def selective_logging (statement):
        if statement.upper().strip().startswith('SELECT'):
            logger.debug(statement)
    with contextlib.closing(sqlite3.connect(url)) as db:
        db.row_factory = sqlite3.Row
        db.set_trace_callback(selective_logging)
        yield db

logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)


from api.services.users.user import router as user_router
app.include_router(user_router) 
