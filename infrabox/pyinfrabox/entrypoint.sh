#!/bin/sh -e
echo "## Run tests"

python /pyinfrabox/test.py

cp coverage.xml /infrabox/upload/coverage/
