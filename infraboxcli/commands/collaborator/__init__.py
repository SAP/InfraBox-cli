import click

from .add_collaborator import add_collaborator
from .change_collaborators_role import change_collaborators_role
from .remove_collaborator import delete_collaborator
from .list_projects_collaborators import list_projects_collaborators


@click.group(name="collab", no_args_is_help=True)
def collaborator():
    """create/list/delete/chg-role collaborators for a project."""
    pass


collaborator.add_command(change_collaborators_role)
collaborator.add_command(add_collaborator)
collaborator.add_command(delete_collaborator)
collaborator.add_command(list_projects_collaborators)
