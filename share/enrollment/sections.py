import boto3, botocore
from dataclasses import dataclass

dynamo_db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Delete table if it already exists
try:
    dynamo_db.Table("sections").delete()
except botocore.exceptions.ClientError:
    pass

table = dynamo_db.create_table(
    TableName = 'sections',
    KeySchema = [ 
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions = [
        {
            "AttributeName": "id",
            "AttributeType": "N"
        }
    ],
    ProvisionedThroughput={
        "ReadCapacityUnits": 10,
        "WriteCapacityUnits": 10,
    },
)

id_counter = 0
@dataclass
class Item:
    class_id: str
    instructor_id: str
    start_date: str
    end_date: str
    days: str
    times: str
    location: str
    max_capacity: int
    is_open: bool
    id: int = 0

    def __post_init__(self):
        if self.id == 0:
            global id_counter
            id_counter += 1
            self.id = id_counter

table.put_item(
    Item = Item(1, 1, '8/19/2023', '12/08/2023', 'Tuesday', '4:00PM to 6:45PM', 'CS 110B - Lecture Room', 1, 1).__dict__
)
table.put_item(
    Item = Item(1, 1, '8/19/2023', '12/08/2023', 'Tuesday', '7:00PM to 9:45PM', 'CS 110B - Lecture Room', 30, 1).__dict__
)
table.put_item(
    Item = Item(2, 1, '8/19/2023', '12/08/2023', 'Thursday', '7:00PM to 9:45PM', 'CS 110B - Lecture Room', 1, 1).__dict__
)
table.put_item(
    Item = Item(2, 1, '8/19/2023', '12/08/2023', 'Thursday', '7:00PM to 9:45PM', 'CS 110B - Lecture Room', 15, 1).__dict__
)