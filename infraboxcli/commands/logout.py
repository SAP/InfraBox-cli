
import click

import infraboxcli


@click.command()
def logout():
    """
    Log's the user out by deleting the user token.
    """

    if infraboxcli.CLI_TOKEN_MANAGER.logout():
        infraboxcli.logger.info("Successfully logged out")
    else:
        infraboxcli.logger.warn("Already logged out")
