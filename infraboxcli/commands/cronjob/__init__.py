import click

from .create_cronjob import create_cronjob
from .delete_cronjob import delete_secret
from .list_projects_cronjobs import list_projects_cronjobs


@click.group(no_args_is_help=True)
def cronjob():
    """create/list/delete cronjobs for a project."""
    pass


cronjob.add_command(create_cronjob)
cronjob.add_command(delete_secret)
cronjob.add_command(list_projects_cronjobs)
