import click

from .abort_job import abort_job
from .clear_job_cache import clear_job_cache
from .download_archive import download_archive
from .job_from_id import job_from_id
from .job_log import get_job_log
from .job_stats import get_job_stats
from .job_testruns import get_job_testruns
from .list_builds_jobs import list_jobs
from .list_jobs_archives import list_jobs_archives
from .pull_job import pull_job
from .restart_job import restart_job


@click.group(no_args_is_help=True)
def job():
    """Job related sub-commands."""
    pass


job.add_command(abort_job)
job.add_command(clear_job_cache)
job.add_command(download_archive)
job.add_command(job_from_id)
job.add_command(get_job_log)
job.add_command(get_job_stats)
job.add_command(get_job_testruns)
job.add_command(list_jobs)
job.add_command(list_jobs_archives)
job.add_command(pull_job)
job.add_command(restart_job)
