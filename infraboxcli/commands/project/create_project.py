import click

import infraboxcli
from v2infraboxapi import ProjectType


@click.command(name="create")
@click.option("-n", "--name", "name", required=True,
              help="The project's name.")
@click.option("-pub", "--public", "public", is_flag=True,
              help="Whether the project should be public (public by default).")
@click.option("-t", "--type", "project_type", default="upload", type=click.Choice(["upload", "gerrit", "github"]),
              help="The project's type (upload by default).")
@click.option("-repo", "--github-repo", "github_repo", default="",
              help="The github repository's name.")
def create_project(name, public, project_type, github_repo):
    """
    Creates a project with, private and of type "upload" by default.
    You can make the project public with the option --public or later use the chg-visibility sub-command.
    You can also change the project's type with the option --type option.
    Do not forget to use the --github-repo option if the project type is "github",
    the format is "github_username/repo_name".
    Also you will first need to authorize the InfraBox server to access your github account.
    This cannot be done with CLI and will need to be done with the web interface.
    \f
    :type name: str
    :param name: the project's name
    :type public: bool
    :param public: whether the project should be public instead of private.
    :type project_type: str
    :param project_type: the project's type: "upload", "gerrit" or "github"
    :type github_repo: str
    :param github_repo: the github repository's name
    """

    if project_type.lower() == "gerrit":
        project_type = ProjectType.GERRIT
    elif project_type.lower() == "github":
        project_type = ProjectType.GITHUB
    else:
        project_type = ProjectType.UPLOAD

    infraboxcli.CLI_SETTINGS.get_api().create_project(name, ProjectType.to_string(project_type), not public,
                                                      github_repo)
    infraboxcli.logger.info("Project created successfully.")
