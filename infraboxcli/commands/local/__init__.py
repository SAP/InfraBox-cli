import click

from .config import config_local_project
from .graph import graph
from .init import init
from infraboxcli.commands.install import install
from .list_jobs import list_local_jobs
from .push import push
from .run import run
from .select import select
from .validate import validate


@click.group(no_args_is_help=True)
def local():
    """Local project related sub-commands."""
    pass


local.add_command(config_local_project)
local.add_command(init)
local.add_command(graph)
local.add_command(install)
local.add_command(list_local_jobs)
local.add_command(push)
local.add_command(run)
local.add_command(select)
local.add_command(validate)
