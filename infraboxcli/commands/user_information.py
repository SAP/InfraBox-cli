import click

import infraboxcli


@click.command("user")
def get_user_information():
    """
    Lists the information about the user currently logged in.
    """
    user = infraboxcli.CLI_SETTINGS.get_api().get_current_user_information()
    print(infraboxcli.tabulate([user.to_string_array("id", "username", "name", "github_id", "email")],
                               headers=["Id", "Username", "Name", "Github Id", "Email"]))
