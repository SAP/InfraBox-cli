import click

import infraboxcli


@click.command(name="create")
@infraboxcli.add_project_id_option
@click.option("-cn", "--cronjob-name", "name", required=True,
              help="The cronjob's name.")
@click.option("-min", "--minute", "minute", required=True,
              help='0 - 59 and valid cron expression ("*", ",", "-").')
@click.option("-h", "--hour", "hour", required=True,
              help='0 - 23 and valid cron expression ("*", ",", "-").')
@click.option("-dm", "--day-month", "day_of_month", required=True,
              help='1 - 31 and valid cron expression ("*", ",", "-").')
@click.option("-m", "--month", "month", required=True,
              help='1 - 12 and valid cron expression ("*", ",", "-").')
@click.option("-dw", "--day-week", "day_of_week", required=True,
              help='0 - 6 and valid cron expression ("*", ",", "-").')
@click.option("-s", "--sha", "sha", required=True,
              help="The git commit's sha or the branch's name.")
@click.option("-f", "--infrabox-file", "infrabox_file", required=True,
              help="The path to the infrabox file.")
def create_cronjob(project_id, name, minute, hour, day_of_month, month, day_of_week, sha, infrabox_file):
    """
    Creates a cronjob (named NAME, with a value of VALUE) for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type name: str
    :param name: the cronjob's name
    :type minute: str
    :param minute: 0 - 59 and valid cron expression ("*", ",", "-")
    :type hour: str
    :param hour: 0 - 23 and valid cron expression ("*", ",", "-")
    :type day_of_month: str
    :param day_of_month: 1 - 31 and valid cron expression ("*", ",", "-")
    :type month: str
    :param month: 1 - 12 and valid cron expression ("*", ",", "-")
    :type day_of_week: str
    :param day_of_week: 0 - 6 and valid cron expression ("*", ",", "-")
    :type sha: str
    :param sha: git commit sha or branch name
    :type infrabox_file: str
    :param infrabox_file: the path to the infrabox file (infrabox.json)
    """

    infraboxcli.CLI_SETTINGS.get_api().create_cronjob(project_id, name, minute, hour, day_of_month,
                                                      month, day_of_week, sha, infrabox_file)
    infraboxcli.logger.info("Cronjob created successfully.")

    infraboxcli.CLI_SETTINGS.save()
