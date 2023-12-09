users-primary: ./bin/litefs mount -config ./etc/litefs/users-primary.yml
users-secondary: ./bin/litefs mount -config ./etc/litefs/users-secondary.yml
users-tertiary: ./bin/litefs mount -config ./etc/litefs/users-tertiary.yml
enrollment: uvicorn --port $PORT api.services.enrollment.main:app --reload
krakend: echo ./etc/krakend.json | entr -nrz krakend run --config etc/krakend.json --port $PORT
amazon-dynamodb-local: java -Djava.library.path=./bin/DynamoDBLocal_lib -jar ./bin/DynamoDBLocal.jar -sharedDb -dbPath ./var/db/enrollment/ -port 8000