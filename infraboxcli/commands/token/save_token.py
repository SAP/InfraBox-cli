import click
import jwt

import infraboxcli


@click.command(name="save")
@click.option("-t", "--token", "token", required=True,
              help="The token.")
@click.option("-h", "--push", "scope_push", is_flag=True,
              help="Whether this token allows to push.")
@click.option("-l", "--pull", "scope_pull", is_flag=True,
              help="Whether this token allows to pull.")
def save_token(token, scope_push, scope_pull):
    """
    Saves a token (already created by any means) for later CLI usage.
    The project's id is inferred from the token.
    Please specify if this token allows to pull/push with their respective options (default: pull=True, push=False).
    \f
    :type token: str
    :param token: a token
    :type scope_push: bool
    :param scope_push: whether this token allows to push
    :type scope_pull: bool
    :param scope_pull: whether this token allows to pull
    """

    # Getting the project_id or storing it
    project_id = jwt.decode(token, verify=False, algorithms=['RS256'])["project"]["id"]

    infraboxcli.CLI_TOKEN_MANAGER.save_token(project_id, token, pull=scope_pull, push=scope_push)

    infraboxcli.logger.info("Token successfully saved for project id: " + project_id)

    # Saving the id in the env/history
    infraboxcli.CLI_SETTINGS.get_from_env(project_id, "project_id")
    infraboxcli.CLI_SETTINGS.save()
