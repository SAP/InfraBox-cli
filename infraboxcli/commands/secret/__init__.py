import click

from .create_secret import create_secret
from .delete_secret import delete_secret
from .list_projects_secrets import list_projects_secrets


@click.group(no_args_is_help=True)
def secret():
    """create/list/delete secrets for a project."""
    pass


secret.add_command(create_secret)
secret.add_command(delete_secret)
secret.add_command(list_projects_secrets)
