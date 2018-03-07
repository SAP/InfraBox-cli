#!/bin/sh -e
echo "## Run tests"

coverage run --source=.,/pyinfrabox --branch test.py
coverage report -m
coverage xml

cp coverage.xml /infrabox/upload/coverage/
