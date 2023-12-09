#!/bin/sh

response=$(curl -s -L -X GET "http://localhost:5400/api/verify?username=jimbo&password=test" -H "accept: application/json")

# Extract the access token from the JSON response using grep and awk
token=$(echo "$response" | grep -o '"access_token":"[^"]*' | awk -F ':"' '{print $2}')

# Check if the token is successfully retrieved
if [ -z "$token" ]; then
  echo "Failed to retrieve the token."
  exit 1
fi

# Use the token to access the protected API and test the methods
#curl -i -L -H "Authorization: Bearer $token" -X GET "http://localhost:5400/api/student/classes/"
# Enroll a Student into a Section
#curl -i -L -H "Authorization: Bearer $token" -X POST "http://localhost:5400/api/student/enroll/?section_id=3&id=1"
# Attempt to Enroll a Student into a Section that is full
curl -i -L -H "Authorization: Bearer $token" -X POST "http://localhost:5400/api/student/enroll/?section_id=4&id=400"
# Check Waitlist Position
#curl -i -L -H "Authorization: Bearer $token" -X GET "http://localhost:5400/api/student/check_waitlist/?section_id=4&id=1"
# Drop From a Class
#curl -i -L -H "Authorization: Bearer $token" -X PUT "http://localhost:5400/api/student/drop/?section_id=4&id=1"
