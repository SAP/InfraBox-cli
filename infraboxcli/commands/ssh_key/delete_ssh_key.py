import click

import infraboxcli


@click.command(name="delete")
@infraboxcli.add_project_id_option
@click.option("-k", "--key-id", "secret_id", required=True,
              help="The SSH key's id.")
def delete_ssh_key(project_id, ssh_key_id):
    """
    Deletes the secret SECRET_ID for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type ssh_key_id: str
    :param ssh_key_id: the key's id
    """

    infraboxcli.CLI_SETTINGS.get_api().delete_sshkey(project_id, ssh_key_id)
    infraboxcli.logger.info("SSH key deleted successfully.")

    infraboxcli.CLI_SETTINGS.save()
