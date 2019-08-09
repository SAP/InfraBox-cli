import click

import infraboxcli


@click.command(name="create")
@infraboxcli.add_project_id_option
@click.option("-sn", "--secret-name", "name", required=True,
              help="The secret's name.")
@click.option("-v", "--value", "value", required=True,
              help="The secret's value.")
def create_secret(project_id, name, value):
    """
    Creates a secret (named NAME, with a value of VALUE) for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type name: str
    :param name: the secret's name
    :type value: str
    :param value: the secret's value
    """

    infraboxcli.CLI_SETTINGS.get_api().create_secret(project_id, name, value)
    infraboxcli.logger.info("Secret created successfully.")

    infraboxcli.CLI_SETTINGS.save()
