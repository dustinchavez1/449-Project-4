curl -i -L -H "Authorization: Bearer $token" -X POST "http://localhost:5400/api/registrar/classes?name=cpsc-120&description=Intro-to-Programming&units=3"

curl -i -L -H "Authorization: Bearer $token" -X POST "http://localhost:5400/api/registrar/sections?class_id=1&instructor_id=1&start_date=10/12/2023&end_date=11/11/2023&days=Monday&times=9:30AM+to+12:15PM&location=CS300&max_capacity=40"


curl -i -L -H "Authorization: Bearer $token" -X DELETE "http://localhost:5400/api/registrar/remove_section?section_id=1"

curl -i -L -H "Authorization: Bearer $token" -X PUT "http://localhost:5400/api/registrar/change_instructor?section_id=1&instructor_id=1"


curl -i -L -H "Authorization: Bearer $token" -X PUT "http://localhost:5400/api/registrar/freeze_autoenrollment?section_id=1"


