#!/bin/sh
echo "## Run tests"

coverage run --source=.,/pyinfrabox --branch test.py

rc=$?

set -e
coverage report -m
coverage xml

cp coverage.xml /infrabox/upload/coverage/

exit $rc
