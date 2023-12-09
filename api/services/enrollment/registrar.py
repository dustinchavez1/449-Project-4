import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Query
from share.enrollment.classes import Item as ClassItem
from share.enrollment.sections import Item as SectionItem
from share.enrollment.waitlist import (
   createWaitlist, deleteWaitlist
)
from api.services.enrollment.main import (
    get_db, validate_registrar_id, validate_section_id, validate_instructor_id
)

router = APIRouter()
            
@router.get("/registrar/classes")
def list_classes(
    id: int = Depends(validate_registrar_id),
    db: boto3.session.Session = Depends(get_db)
):
    classes = db.Table("classes").scan()["Items"]
    return {"classes": classes}

@router.post("/registrar/classes")
def create_class(
    name: str,
    description: str,
    # greater than or equal to atleast 1 unit
    units: int = Query(..., ge=1, description="Number of units (non-negative integer)"),
    db: boto3.session.Session = Depends(get_db)
):
    try:
     table = db.Table('classes')  
     table.put_item(
        Item=ClassItem(name, description, units).__dict__
    )
     return {"message": "Successfully created class with name {name}"}
    except ClientError as err:
     raise HTTPException(status_code=400, detail=f"Error: {str(err)}")
    
@router.post("/registrar/sections")
def create_section(
    class_id: int,
    instructor_id: int,
    start_date: str,  
    end_date: str,  
    days: str,
    times: str,
    location: str,
    max_capacity: int,
    id: int = Depends(validate_registrar_id),
    db: boto3.session.Session = Depends(get_db)
):
   
    try:
      db.Table('sections').put_item(Item=SectionItem(class_id,instructor_id,start_date,end_date,days,times,location,max_capacity,1).__dict__)
      # Creates the Waitlist for the Newly Created Section
      createWaitlist(id)
      return {"message": "Successfully Created Section"}
    	
    except ClientError as err:
        raise HTTPException(status_code=400, detail=f"Error: {str(err)}")
    
# Method to delete existing section from class       
@router.delete("/registrar/remove_section")
def remove_section(
    section_id: int,
    id: int = Depends(validate_registrar_id),
    db: boto3.session.Session = Depends(get_db)
):
    # Validate section
    section_id = validate_section_id(section_id, db)
    
    # Delete section
    db.Table('sections').delete_item(
       Key={
        "id": section_id
      }
    )
 
    # Delete enrollments associated with this section id
    section_enrollments = db.Table('enrollments').query(
      KeyConditionExpression=Key('section_id').eq(section_id)
    )

    # Don't Delete if there's No Enrollments for the Section (No Enrollments in the Class - There are no Section Entries) 
    if section_enrollments['Items'] == []:
      pass
    else:
      for item in section_enrollments['Items']:
        db.Table('enrollments').delete_item(
          Key={
              'section_id': item['section_id'], 
              'student_id': item['student_id']
            }
        )
    # Delete Waitlist for the Section
    deleteWaitlist(section_id)
    return {"message": "Successfully deleted section", "section_id": str(section_id)}

# Method to change instructor for a particular section
@router.put("/registrar/change_instructor")	
def change_instructor_for_section(
  section_id: int,
  instructor_id: int,
  id: int = Depends(validate_registrar_id),
  db: boto3.session.Session = Depends(get_db)
):
# Validate section and instructor
  section_id = validate_section_id(section_id, db)
  instructor_id = validate_instructor_id(instructor_id, db)  
  response = db.Table('sections').update_item(
    Key={
        'id': section_id
    },
    UpdateExpression="SET instructor_id = :value1",
    ExpressionAttributeValues={
      ':value1': instructor_id
    },
    ReturnValues="UPDATED_NEW"
    )    
  return {"message": "Successfully changed the instructor with id " + str(instructor_id) + " for section with section ID "+  str(section_id)}
  

# Method to freeze the automatic enrollment from second week of classes
@router.put("/registrar/freeze_autoenrollment")
def freeze_autoenrollment(
    section_id: int,
    db: boto3.session.Session = Depends(get_db)
):
    # Validate section
  section_id = validate_section_id(section_id, db)

    # Update sections table close the enrollment to that section
  response = db.Table('sections').update_item(
    Key={
      'id': section_id
    },
    UpdateExpression="SET is_open = :value1",
    ExpressionAttributeValues={
      ':value1': 0
    },
    ReturnValues="UPDATED_NEW"
    )
  return {"message": "Successfully frozen the automatic enrollment to section with id " + str(section_id) + " during second week of class"}
  

