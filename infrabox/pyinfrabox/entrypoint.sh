#!/bin/sh -e

mkdir -p /infrabox/upload/badge
mkdir -p /infrabox/upload/markup

echo "## Run tests"
nosetests --with-coverage --cover-xml --cover-branches --cover-package=pyinfrabox --cover-tests tests/*

echo "## Download coverage"
git clone https://github.com/InfraBox/coverage.git /tmp/coverage

echo "## Create coverage result"
export PYTHONPATH=/
python /tmp/coverage/coverage.py --output /infrabox/upload/markup/coverage.json --input coverage.xml --badge /infrabox/upload/badge/coverage.json --format py-coverage
