import click

import infraboxcli


@click.command(name="create")
@infraboxcli.add_project_id_option
@click.option("-kn", "--key-name", "name", required=True,
              help="The SSH key's name.")
@click.option("-sn", "--secret-name", "secret_name", required=True,
              help="The secret's name.")
def create_ssh_key(project_id, name, secret_name):
    """
    Creates a SSH key (named NAME, with a value of VALUE) for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type name: str
    :param name: the key's name
    :type secret_name: str
    :param name: the secret's name
    """

    infraboxcli.CLI_SETTINGS.get_api().create_sshkey(project_id, name, secret_name)
    infraboxcli.logger.info("SSH key created successfully.")

    infraboxcli.CLI_SETTINGS.save()
