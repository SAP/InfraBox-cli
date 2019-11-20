import click

import infraboxcli


@click.command(name="list")
@infraboxcli.add_project_id_option
def list_projects_cronjobs(project_id):
    """
    Lists the project's cronjobs for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    cronjobs = [cronjob.to_string_array("name", "id", "minute", "hour", "day_of_week", "month",
                                        "day_of_month", "sha", "infrabox_file")
                for cronjob in infraboxcli.CLI_SETTINGS.get_api().get_projects_cronjobs(project_id)]
    print(infraboxcli.tabulate(cronjobs, headers=["Name", "Id", "Minute", "Hour", "Day of week", "Month",
                                                  "Day of month", "Sha", "InfraBox file"]))

    infraboxcli.CLI_SETTINGS.save()
