import boto3
from boto3.dynamodb.conditions import Key
import datetime
from fastapi import APIRouter, Depends, HTTPException
from share.enrollment.enrollments import Item as Enrollment
from share.enrollment.waitlist import (
    addWaitlists, checkWaitlistPosition, checkWaitlistSize, removeWaitlist, removeAndAddWaitlist, checkNumberOfWaitlistEnrollments, createWaitlist
)
from share.enrollment.enrollment_count import (
    addSectionEnrollment, checkCurrentSectionSize
)

from api.services.enrollment.main import (
    get_db, validate_student_id, validate_section_id
)

router = APIRouter()

# List all classes
@router.get("/student/classes")
def list_classes(
    id: int = Depends(validate_student_id),
    db: boto3.session.Session = Depends(get_db)
):
    sections = db.Table("sections").scan()["Items"]
    return {"sections": sections}

# Return section and position that student is waitlisted in
@router.get("/student/check_waitlist")
def check_waitlist(
     section_id: int,
     id: int = Depends(validate_student_id),
):
    try:
        response = checkWaitlistPosition(section_id, id)
        if response == None:
            response = 0
        return {"Student of ID #: ": str(id), "waitlisted in section #: ": str(section_id), "with position": str(response)}
    except LookupError:
        raise HTTPException(status_code=404, detail="Student is not in this Waitlisted Class")


# # # Enroll student into section or into section's waitlist
@router.post("/student/enroll")
def enroll_student(
    section_id: int,
    id: int = Depends(validate_student_id), 
    db: boto3.session.Session = Depends(get_db)
    ):
    
    section_id = validate_section_id(section_id, db)

    # Check if student with given id is not enrolled already
    result = db.Table("enrollments").query(
        KeyConditionExpression=Key('section_id').eq(section_id) & Key('student_id').eq(id)
    )

    if result["Items"] != []:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this class")

    # Gets current capacity of students; actively in the class
    current_capacity = checkCurrentSectionSize(section_id)

    # If current_capacity is None, then there are no students in the class
    if current_capacity == None:
        current_capacity = 0
    else:
        current_capacity = int(current_capacity)
    
    max_capacity = db.Table("sections").query(
        KeyConditionExpression=Key("id").eq(section_id),
    )

    max_capacity = max_capacity["Items"][0]["max_capacity"]
    max_capacity = int(max_capacity)

    # If current_capacity == max_capacity, then class is full.
    if current_capacity >= max_capacity:

        # Creates the waitlist if it does not exist
        createWaitlist(section_id)
        
        # get Waitlisted Count
        waitlist_count = checkWaitlistSize(section_id)

        # Check if waitlist is ful;
        if waitlist_count >= 15:
            raise HTTPException (status_code=400,detail="Waitlist is full. There are 15 students already waitlisted.")

        # get amount of classes student is waitlisted in
        num_waitlisted = checkNumberOfWaitlistEnrollments(id)
        # Raise Error if Student is Already Waitlisted in 3 Classes
        if num_waitlisted == 3:
            raise HTTPException (status_code=400,detail="Student is already waitlisted in 3 classes.")

        # Enroll Student into the class as waitlisted
        addWaitlists(section_id, id)
        position = checkWaitlistPosition(section_id, id)
        if position == None:
            position = 0
  
        return {"details": f"The class is currently full you are waitlisted at number {position}"}

    # Inserts the student into enrollments table if there is space in the class
    else:
        try:
            # Add Student to Enrollments Table
            db.Table("enrollments").put_item(
                Item=Enrollment(id, section_id, datetime.datetime.now().strftime("%m/%d/%Y"), 0).__dict__
            )
            # Icrement Section Enrollment Counter
            addSectionEnrollment(section_id)

            return {"details": "Student of id " + str(id) + " sucessfully enrolled"}
        
        # Check if enroll was successful
        except:
            raise HTTPException(status_code=400,detail="Student was unable to be enrolled in section_id: " + str(section_id))
        

# # Drop Student from a Class
@router.put("/student/drop")
def drop_class(
    section_id: int, 
    id: int = Depends(validate_student_id),
    db: boto3.session.Session = Depends(get_db)
    ):

    # Check if section exists
    section_id = validate_section_id(section_id, db)

    # Check whether or not a student is enrolled in the section
    result = db.Table("enrollments").query(
        KeyConditionExpression=Key('section_id').eq(section_id) & Key('student_id').eq(id)
    )

    # Confirms that student is not enrolled in the class and is not waitlisted in the class
    if result["Items"][0]["is_dropped"] == 1 and checkWaitlistPosition(section_id, id) == None:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this class")
    
    else:
        # Determines if student is waitlisted in the class    
        result = checkWaitlistPosition(section_id, id)
        if result == None:
        # Switch Student From is_dropped FALSE (or UNSET) to TRUE in Enrollments Table also set is_waitlisted to FALSE
            db.Table("enrollments").update_item(
                Key={
                    'section_id': section_id,
                    'student_id': id
                },
                UpdateExpression="SET is_dropped = :r",
                ExpressionAttributeValues={
                    ":r": 1
                },
                ReturnValues="UPDATED_NEW"                                   
            )
            addSectionEnrollment(section_id, -1)
        else:
            removeWaitlist(section_id, id)

    # If drop is successful We want to move the first person in waitlist to enrolled if they exist
    try:
        student_id_to_enroll = removeAndAddWaitlist(section_id)[0][0]
        student_id_to_enroll = int(student_id_to_enroll)

                # If student exists on waitlist

        # Add Student to Enrollments Table
        db.Table("enrollments").put_item(
            Item=Enrollment(student_id_to_enroll, section_id, datetime.datetime.now().strftime("%m/%d/%Y"), 0).__dict__
        )
        # Icrement Section Enrollment Counter
        addSectionEnrollment(section_id)

        return {"details": "Student of id " + str(id) + " sucessfully dropped and student of id " + str(student_id_to_enroll) + " enrolled"}
    
    except:
        return {"details":"Student# " + str(id) + " dropped from " + str(section_id)}

    
    