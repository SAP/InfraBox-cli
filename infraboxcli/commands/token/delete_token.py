import click

import infraboxcli


@click.command(name="delete")
@infraboxcli.add_project_id_option
@click.option("-t", "--token-id", "token_id", required=True,
              help="The token's id.")
def delete_token(project_id, token_id):
    """
    Deletes the secret TOKEN_ID for a PROJECT_ID.
    Will not delete local saves of the token.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type token_id: str
    :param token_id: the token's id
    """

    infraboxcli.CLI_SETTINGS.get_api().delete_token(project_id, token_id)
    infraboxcli.logger.info("Token deleted successfully.")

    infraboxcli.CLI_SETTINGS.save()
