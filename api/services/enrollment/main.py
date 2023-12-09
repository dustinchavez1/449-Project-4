import contextlib
import logging.config
import boto3

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env", extra="ignore"):
    enrollment_database: str
    logging_config: str


settings = Settings()
app = FastAPI()

def get_logger():
    return logging.getLogger(__name__)

def get_db():
    return boto3.resource('dynamodb', endpoint_url=settings.enrollment_database)

def validate_instructor_id(
    req: Request,
    id: int = None,
    db: boto3.session.Session = Depends(get_db)
):
    if id is None:
        username = req.headers.get("x-username")
        users = db.Table("instructors").scan(AttributesToGet=['id', 'username'])["Items"]
        user = next((_ for _ in users if _.get("username") == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail="Instructor of username " + str(username) + " not found")
        id = user["id"]
    else:
        if db.Table("instructors").get_item(Key={"id": id}) is None:
            raise HTTPException(status_code=404, detail="Instructor of id " + str(id) + " not found")
    return id


def validate_student_id(
    req: Request,
    id: int = None,
    db: boto3.session.Session = Depends(get_db)
):
    if id is None:
        username = req.headers.get("x-username")
        users = db.Table("students").scan(AttributesToGet=['id', 'username'])["Items"]
        user = next((_ for _ in users if _.get("username") == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail="Student of username " + str(username) + " not found")
        id = user["id"]
    else:
        if db.Table("students").get_item(Key={"id": id}) is None:
            raise HTTPException(status_code=404, detail="Student of id " + str(id) + " not found")
    return id

def validate_registrar_id(
    req: Request,
    id: int = None,
    db: boto3.session.Session = Depends(get_db)
):
    if id is None:
        username = req.headers.get("x-username")
        users = db.Table("registrar").scan(AttributesToGet=['id', 'username'])["Items"]
        user = next((_ for _ in users if _.get("username") == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail="Registar of username " + str(username) + " not found")
        id = user["id"]
    else:
        if db.Table("registrar").get_item(Key={"id": id}) is None:
            raise HTTPException(status_code=404, detail="Registar of id " + str(id) + " not found")
    return id

def validate_section_id(
    id: int, 
    db: boto3.session.Session = Depends(get_db)
):
    if db.Table("sections").get_item(Key={"id": id}) is None:
        raise HTTPException(status_code=404, detail="Section of id " + str(id) + " not found")
    return id


logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)

from api.services.enrollment.student import router as student_router
app.include_router(student_router) 

from api.services.enrollment.instructor import router as instructor_router
app.include_router(instructor_router) 

from api.services.enrollment.registrar import router as registrar_router
app.include_router(registrar_router) 

