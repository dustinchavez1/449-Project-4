from fastapi import Depends, FastAPI, HTTPException, Path
import redis
from share.notifications.notifications import (get_subscriptions, delete_subscription)


router = APIRouter()

redis_connection_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

@router.post("/subscribe/add_course")
def subscribe_to_new_course(
    student_id: Depends(validate_student_id),
    section_id: Depends(validate_section_id),
    email: str,
    web_hook: str
):
    return

@router.get("/subscribe/list_notifications")
def list_subscriptions(
    student_id: Depends(validate_student_id)
):
    #Return a list of a student_id classes
    subscriptions = get_subscriptions(student_id)
    return {"Subscriptions": subscriptions}

@router.delete("/subscribe/delete_notification")
def delete_subscriptions(
    student_id: Depends(validate_student_id),
    section_id: Depends(validate_section_id)
):
    response = delete_subscription(student_id, section_id)
    return {"Element removed": response}