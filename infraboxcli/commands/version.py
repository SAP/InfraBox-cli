import click


@click.command()
def version():
    """
    Displays the CLI's version.
    """
    print("infraboxcli " + CLI_VERSION)


CLI_VERSION = "2.0"
