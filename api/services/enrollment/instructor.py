import boto3
from boto3.dynamodb.conditions import Key, Attr
from fastapi import APIRouter, Depends, HTTPException
from share.enrollment.waitlist import (
    displayWaitlist, removeAndAddWaitlist
)

from api.services.enrollment.main import (
    get_db, validate_student_id, validate_instructor_id, validate_section_id
)
from api.utils import join

router = APIRouter()

# List all the sections where the instructor teaches
@router.get("/instructor/enrollment")
def list_student_enrollment(
    id: int = Depends(validate_instructor_id),
    db: boto3.session.Session = Depends(get_db)
):
    sections = db.Table("sections").scan()["Items"]
    instuctor_sections = [_ for _ in sections if _["instructor_id"] == id]
    return {"sections": instuctor_sections}


@router.post("/instructor/drop")
def drop_student(
    student_id: int,
    section_id: int,
    id: int = Depends(validate_instructor_id),
    db: boto3.session.Session = Depends(get_db)
):
    student_id = validate_student_id(student_id, db)
    section_id = validate_section_id(section_id, db)

    # Check if instructor is teaching the section
    result = db.Table("sections").query(
        KeyConditionExpression=Key('id').eq(section_id) 
      )
    
    if result["Items"] != []:
        pass
    else:
        raise HTTPException(status_code=400, detail="Instructor does not teach section_id: " + str(section_id))

    # Check if student is enrolled in the section
    result = db.Table("enrollments").query(KeyConditionExpression=Key('section_id').eq(section_id) & Key('student_id').eq(student_id))
    if result == []:
        raise HTTPException(status_code=400,detail="Student was not found to be enrolled in section_id: " + str(section_id))
    else:
        if result["Items"][0]["is_dropped"] == 1: 
            raise HTTPException(
                status_code=400,
                detail="Student was already dropped from section_id: " + str(section_id)
            )

    # Drop a student from class. Update student's enrollment column 'is_dropped'.
    db.Table("enrollments").update_item(
        Key={
            'section_id': section_id,
            'student_id': student_id
        },
        UpdateExpression="SET is_dropped = :value1",
        ExpressionAttributeValues={
            ':value1': 1
        }
    )

    return {"details": "Dropped student of id " + str(student_id) + ", from section of id " + str(section_id)}

# List all students who dropped from a given section_id
@router.get("/instructor/dropped")
def list_dropped_students(
    section_id: int,
    id: int = Depends(validate_instructor_id),
    db: boto3.session.Session = Depends(get_db)
):
    section_id = validate_section_id(id=section_id, db=db)

    enrollments = db.Table("enrollments").query(
        KeyConditionExpression=Key("section_id").eq(section_id),
        FilterExpression=Attr("is_dropped").eq(1)
    )

    dropped = []

    if len(enrollments["Items"]) == 1:
        student = db.Table("students").query(
            KeyConditionExpression=Key("id").eq(enrollments["Items"][0]["student_id"])
        )
        student_name = student["Items"][0]["name"]
        dropped.append({"Student Id": enrollments["Items"][0]["student_id"], "Name": student_name})
    else:
        for students in enrollments["Items"]:
            student_id = students["student_id"]
            student = db.Table("students").query(
                KeyConditionExpression=Key("id").eq(student_id)
            )
            student_name = student["Items"][0]["name"]
            dropped.append({"Student Id": student_id, "Name": student_name})

    return {"students": dropped}    


@router.get("/instructor/waitlisted")
def list_waitlisted_students(
    section_id: int,
    id: int = Depends(validate_instructor_id),
    db: boto3.session.Session = Depends(get_db)
):
    section_id = validate_section_id(id=section_id, db=db)

    waitlisted = displayWaitlist(section_id)

    waitlist = []

    for position, x in enumerate(waitlisted):
        student_id = int(x)
        student = db.Table("students").query(
            KeyConditionExpression=Key("id").eq(student_id)
        )
        student_name = student["Items"][0]["name"]
        waitlist.append({"Student Id": student_id, "Name": student_name, "Position": position + 1})
    
    # Returns Students in Waitlist or Return 400 Error if Waitlist is Empty / D.N.E.
    if waitlist:
        return {"students": waitlist}
    else: 
        raise HTTPException(status_code=400, detail="There are currently no students in the waitlist")