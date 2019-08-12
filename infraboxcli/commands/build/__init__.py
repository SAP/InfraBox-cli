import click

from .abort_build import abort_build
from .build_from_id import build_from_id
from .clear_build_cache import clear_job_cache
from .list_projects_builds import list_builds
from .restart_build import restart_build
# from .upload_build import upload_build


@click.group(no_args_is_help=True)
def build():
    """Build related sub-commands."""
    pass


build.add_command(abort_build)
build.add_command(build_from_id)
build.add_command(clear_job_cache)
build.add_command(list_builds)
build.add_command(restart_build)
# build.add_command(upload_build)
