import click

import infraboxcli


@click.command(name="list")
@infraboxcli.add_project_id_option
def list_projects_tokens(project_id):
    """
    Lists the project's tokens for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    tokens = [secret.to_string_array("description", "id", "scope_push", "scope_pull")
              for secret in infraboxcli.CLI_SETTINGS.get_api().get_projects_tokens(project_id)]
    print(infraboxcli.tabulate(tokens, headers=["Description", "Id", "Allows to push", "Allows to pull"]))

    infraboxcli.CLI_SETTINGS.save()
