import json
import boto3, botocore
from dataclasses import dataclass

dynamo_db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Delete table if it already exists
try:
    dynamo_db.Table("classes").delete()
except botocore.exceptions.ClientError:
    pass

table = dynamo_db.create_table(
    TableName = 'classes',
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
    name: str
    description: str
    units: int
    id: int = 0

    def __post_init__(self):
        if self.id == 0:
            global id_counter
            id_counter += 1
            self.id = id_counter

table.put_item(
    Item = Item("CPSC449", "Web Back-End Engineering", 3).__dict__
)
table.put_item(
    Item = Item("CPSC458", "Malware Analysis", 3).__dict__
)
table.put_item(
    Item = Item("CPSC471", "Computer Communications", 3).__dict__
)

# Debug print output
#print(json.dumps(table.scan()["Items"], indent=2, default=str))