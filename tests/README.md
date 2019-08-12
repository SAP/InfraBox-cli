# Tests

## Requirements

This test suite can be launched through the `cli_test.py` script.
It requires the URL to a running InfraBox server and the credentials for a test user.
Two bash scripts are also provided to install a local InfraBox server using `minikube` and `kvm2`.
The admin credentials for the InfraBox server created this way are simply `admin@admin.com` and `admin`.

## Usage

The `cli_test.py` script can be used as a CLI.
Simply use the `--url`, `--email`, and `--password` options to specify the required information.
