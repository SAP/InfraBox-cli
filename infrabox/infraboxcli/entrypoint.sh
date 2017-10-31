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

cd examples

# validate examples
echo "## validate 1_hello_world"
cd 1_hello_world
infrabox validate
cd ..

echo "## validate 2_dependencies"
cd 2_dependencies
infrabox validate
cd ..

echo "## validate 3_testresult"
cd 3_testresult
infrabox validate
cd ..

echo "## validate 5_keep"
cd 5_keep
infrabox validate
cd ..

echo "## validate 6_dependency_conditions"
cd 6_dependency_conditions
infrabox validate
cd ..
