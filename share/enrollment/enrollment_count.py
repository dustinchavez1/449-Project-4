# Used in-place of COUNT(*) in SQL as there is no equivalent in Amazon DynamoDB
import redis 

redis_connection_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

sections = "Sections"

def addSectionEnrollment(section_id, increment=1):
    r = redis.Redis(connection_pool=redis_connection_pool)
    r.hincrby(sections, section_id, increment)

def checkCurrentSectionSize(section_id):
    r = redis.Redis(connection_pool=redis_connection_pool)
    return r.hget(sections, section_id)

# This is here due to the enrollments.py having test data put into it
addSectionEnrollment(1)
addSectionEnrollment(4)
addSectionEnrollment(1)
addSectionEnrollment(2)
addSectionEnrollment(1)
addSectionEnrollment(2)
addSectionEnrollment(3)
addSectionEnrollment(4, 15)