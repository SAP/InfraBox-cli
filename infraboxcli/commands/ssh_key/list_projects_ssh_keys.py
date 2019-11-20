import click

import infraboxcli


@click.command(name="list")
@infraboxcli.add_project_id_option
def list_projects_ssh_keys(project_id):
    """
    Lists the project's SSH keys for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    secrets = [key.to_string_array("name", "id", "secret_name")
               for key in infraboxcli.CLI_SETTINGS.get_api().get_projects_sshkeys(project_id)]
    print(infraboxcli.tabulate(secrets, headers=["Name", "Id", "Secret's name"]))

    infraboxcli.CLI_SETTINGS.save()
