import redis

redis_connection_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

waitlists = "Waitlists"

# Creates a Waitlist for a Section - Registar API Call
def createWaitlist(section_id):
    r = redis.Redis(connection_pool=redis_connection_pool)
    r.sadd(waitlists, str(section_id))

# Adds a Student to the Waitlist and Creates Waitlist if None Exists for that Class - Student API Call
def addWaitlists(class_waitlist, id):
        r = redis.Redis(connection_pool=redis_connection_pool)
        if r.sismember(waitlists, class_waitlist) == 1:
            position = r.zcard(class_waitlist) + 1
            r.zadd(class_waitlist, {id: position})   # Adds Student to Waitlist with Position Number in order to Track Users By Position 'Score' - Not Used to Track actual position (use rank instead)
        else:
            raise LookupError("Waitlist Does Not Exist")

# Prints the Waitlist with the Positions of Each Student - Instructor API Call
def displayWaitlist(selected_waitlist):
    r = redis.Redis(connection_pool=redis_connection_pool)
    selected_waitlist = str(selected_waitlist)
    if r.sismember(waitlists, selected_waitlist) == 1:    # Error Checks to See if Waitlist Exists
        return r.zrange(selected_waitlist, 0, -1)
    else:
        raise LookupError("Waitlist Does Not Exist")

# Checks the Waitlist Position of a Student - Student API Call
def checkWaitlistPosition(selected_waitlist, id):
    r = redis.Redis(connection_pool=redis_connection_pool)
    if r.sismember(waitlists, str(selected_waitlist)) == 1:
        return r.zrank(str(selected_waitlist), id)          # Starts with '0' index; starting with '1' for normal users
    else:
        raise LookupError("Waitlist Does Not Exist")
        
# Checks the Waitlist Size to See if it is Full and Whether or Not a Student Can be Added - Student API Call
def checkWaitlistSize(selected_waitlist):
    r = redis.Redis(connection_pool=redis_connection_pool)
    return r.zcard(selected_waitlist)

# Checks to See if a Student is Waitlisted in More than 3 Classes - Student API Call
def checkNumberOfWaitlistEnrollments(id):
    r = redis.Redis(connection_pool=redis_connection_pool)
    class_waitlists = r.smembers(waitlists)
    count = 0 
    for waitlist in class_waitlists:
        if r.zscore(waitlist, id) is not None:
            count += 1
    return count

# Removes a Student From the Waitlist when Dropping or Being Dropped - Instructor or Student API Call
def removeWaitlist(selected_waitlist, id):
    r = redis.Redis(connection_pool=redis_connection_pool)
    try: 
        r.zrem(selected_waitlist, id)    
    except:
        raise LookupError("Student Does Not Exist in Waitlist")

# Similar to removeWaitlist, but also pulls the student to be enrolled in the class - Student API Call
def removeAndAddWaitlist(selected_waitlist):
    r = redis.Redis(connection_pool=redis_connection_pool)
    try: 
        return r.zpopmin(selected_waitlist)
    except:
        raise LookupError("Student Does Not Exist in Waitlist")
    
# Deletes a Waitlist - Registrar API Call
def deleteWaitlist(selected_waitlist):
    r = redis.Redis(connection_pool=redis_connection_pool)
    try:
        r.srem(waitlists, selected_waitlist)
        r.zremrangebyrank(selected_waitlist, 0, -1)
    except:
        raise LookupError("Waitlist Does Not Exist")