#!/bin/sh

# Register 'jimbo' as a student user
curl -i -L -X 'POST' \
  'http://127.0.0.1:5400/api/register/?username=jimbo&password=test&roles=1' \
  -H 'accept: application/json' \
  -d '' \

# Register 'avery' as an instructor user
curl -i -L -X 'POST' \
  'http://127.0.0.1:5400/api/register/?username=avery&password=test&roles=2' \
  -H 'accept: application/json' \
  -d '' \

# Register 'admin' as a registrar user
curl -i -L -X 'POST' \
  'http://127.0.0.1:5400/api/register/?username=admin&password=test&roles=3' \
  -H 'accept: application/json' \
  -d '' \
