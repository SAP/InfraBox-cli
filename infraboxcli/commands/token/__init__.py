import click

from .create_token import create_token
from .delete_token import delete_token
from .list_local_tokens import list_local_tokens
from .list_projects_tokens import list_projects_tokens
from .local_delete_token import local_delete_token
from .save_token import save_token


@click.group(no_args_is_help=True)
def token():
    """create/list/delete tokens for a project."""
    pass


token.add_command(create_token)
token.add_command(delete_token)
token.add_command(list_local_tokens)
token.add_command(list_projects_tokens)
token.add_command(local_delete_token)
token.add_command(save_token)
