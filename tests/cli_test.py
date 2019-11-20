#!/usr/bin/env python
import os
import unittest

import click

import infraboxcli
from infraboxcli.commands.install import get_host
from tests_infraboxcli.commands import Utils


@click.command()
@click.option("-u", "--url", "url", default=None,
              help="The remote's url.")
@click.option("-e", "--email", "email", required=True,
              help="The test account's email.")
@click.option("-p", "--password", "password",  required=True,
              help="The test account's password.")
def cli(url, email, password):
    # Setup the host for tests
    if os.path.isfile("./.cli_settings"):
        os.remove("./.cli_settings")

    infraboxcli.CLISettings._SAVE_PATH = "./.cli_settings"
    infraboxcli.CLI_SETTINGS._SAVE_PATH = "./.cli_settings"

    infraboxcli.CLITokenManager._LOGIN_TOKEN_PATH = "./.login.token"
    infraboxcli.CLI_TOKEN_MANAGER._LOGIN_TOKEN_PATH = "./.login.token"

    infraboxcli.CLI_SETTINGS = infraboxcli.CLI_SETTINGS.load()

    try:
        infraboxcli.CLI_SETTINGS.infrabox_url = "https://" + get_host() if url is None else url
    except:
        pass

    if email is not None:
        Utils.USER_EMAIL = email
    if password is not None:
        Utils.USER_PASSWORD = password

    test_suite = unittest.TestLoader().discover('.', pattern="test_*.py")
    unittest.TextTestRunner(verbosity=0, buffer=True).run(test_suite)

    infraboxcli.CLI_TOKEN_MANAGER.logout()
    if os.path.isfile("./.cli_settings"):
        os.remove("./.cli_settings")


if __name__ == '__main__':
    cli()
