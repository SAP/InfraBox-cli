#!/bin/sh -e
find /infraboxcli -name \*.pyc -delete

# test help
echo "## Test --help"
infrabox --help

# test list
echo "## Test list"
infrabox list

# test validate
echo "## Test validate"
infrabox validate
