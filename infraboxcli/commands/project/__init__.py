import click

from .change_visibility import change_project_visibility
from .create_project import create_project
from .delete_project import delete_project
from .list_users_projects import list_users_projects
from .project_from_id_or_name import project_from_id_or_name
from .trigger_new_build import trigger_new_build


@click.group(no_args_is_help=True)
def project():
    """Project related sub-commands."""
    pass


project.add_command(change_project_visibility)
project.add_command(create_project)
project.add_command(delete_project)
project.add_command(list_users_projects)
project.add_command(project_from_id_or_name)
project.add_command(trigger_new_build)
