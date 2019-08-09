import click

import infraboxcli


@click.command(name="list")
@infraboxcli.add_project_id_option
def list_projects_secrets(project_id):
    """
    Lists the project's secrets for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    secrets = [secret.to_string_array("name", "id")
               for secret in infraboxcli.CLI_SETTINGS.get_api().get_projects_secrets(project_id)]
    print(infraboxcli.tabulate(secrets, headers=["Name", "Id"]))

    infraboxcli.CLI_SETTINGS.save()
