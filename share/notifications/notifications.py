import redis

redis_connection_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

def get_subscriptions(student_id):
    r = redis.Redis(connection_pool= redis_connection_pool)
    subscriptions = r.smembers(f"subscriptions:{student_id}")
    return {s.decode('utf-8') for s in subscriptions}
 
def delete_subscription(student_id, section_id):
    r = redis.Redis(connection_pool = redis_connection_pool)
    response = r.srem(student_id, section_id)
    return(f'Element removed: {response}')
