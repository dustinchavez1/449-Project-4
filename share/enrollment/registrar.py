import boto3, botocore
from dataclasses import dataclass

dynamo_db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Delete table if it already exists
try:
    dynamo_db.Table("registrar").delete()
except botocore.exceptions.ClientError:
    pass

table = dynamo_db.create_table(
    TableName = 'registrar',
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
    username: str
    name: str
    id: int = 0

    def __post_init__(self):
        if self.id == 0:
            global id_counter
            id_counter += 1
            self.id = id_counter

table.put_item(
    Item = Item('admin', 'Jack').__dict__
)