#!/bin/sh -e
find /infraboxcli -name \*.pyc -delete

# test help
echo "## Test --help"
infrabox --help

# test list
echo "## Test list"
infrabox local list

# test validate
echo "## Test validate"
infrabox local validate

cd examples

# validate examples
echo "## validate 1_hello_world"
cd 1_hello_world
infrabox local validate
cd ..

echo "## validate 2_dependencies"
cd 2_dependencies
infrabox local validate
cd ..

echo "## validate 3_testresult"
cd 3_testresult
infrabox local validate
cd ..

echo "## validate 6_dependency_conditions"
cd 6_dependency_conditions
infrabox local validate
cd ..
