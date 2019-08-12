import click

from .create_ssh_key import create_ssh_key
from .delete_ssh_key import delete_ssh_key
from .list_projects_ssh_keys import list_projects_ssh_keys


@click.group(name="ssh-key", no_args_is_help=True)
def ssh_key():
    """create/list/delete SSH keys for a project."""
    pass


ssh_key.add_command(create_ssh_key)
ssh_key.add_command(delete_ssh_key)
ssh_key.add_command(list_projects_ssh_keys)
