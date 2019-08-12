import click

import infraboxcli


@click.command()
@click.option("-e", "--email", "email", required=True,
              help="The user's email address.")
@click.option("-p", "--password", "password", prompt=True, hide_input=True,
              help="The user's password.")
def login(email, password):
    """
    Log's the user in (EMAIL) by storing the user token.
    You can pass your password as an option or type it in the terminal later.
    \f
    :type email: str
    :param email: the user's email
    :type password: str
    :param password: the user's password
    """

    cookies = infraboxcli.CLI_SETTINGS.get_api().login(email, password)

    if "token" in cookies:
        infraboxcli.CLI_TOKEN_MANAGER.login(cookies["token"])
        infraboxcli.logger.info("Login Successful")
    else:
        infraboxcli.logger.error("Login Error")
