#!/bin/sh

response=$(curl -s -L -X GET "http://localhost:5400/api/verify?username=admin&password=test" -H "accept: application/json")

# Extract the access token from the JSON response using grep and awk
token=$(echo "$response" | grep -o '"access_token":"[^"]*' | awk -F ':"' '{print $2}')

# Check if the token is successfully retrieved
if [ -z "$token" ]; then
  echo "Failed to retrieve the token."
  exit 1
fi

curl -i -L -H "Authorization: Bearer $token" -X DELETE "http://localhost:5400/api/registrar/remove_section/?section_id=1"

