import os

import click
from tabulate import tabulate as original_tabulate
import json
from v2infraboxapi import InfraBoxAPIException
from .CLISettings import CLISettings, CLI_SETTINGS
from .CLITokenManager import CLI_TOKEN_MANAGER, CLITokenManager
from .ClickUtils import MutuallyExclusiveOption, add_project_id_option, add_build_id_option, add_job_id_option
from .Utils import CLI_DATA_DIR, InfraBoxCLIException, locked
from .commands import CLI_COMMAND_LIST
from .local_project_dependencies import LocalProjectConfig, show_console, execute, get_job_list, load_infrabox_file, \
    WorkflowCache, ValidationError
from .log import logger, LoggerError


def tabulate(data, headers=None):
    style = CLI_SETTINGS.grid_style

    # Custom style
    if style == "json":
        return json.dumps([{headers[j]: data[i][j] for j in range(len(headers))} for i in range(len(data))])

    """Module wide wrapper for tabulate. Used to set the table format easily."""
    return original_tabulate(data, headers=headers, tablefmt=style)


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option("-s", "--grid-style", "grid_style", default=None, type=click.Choice(
    choices=['fancy_grid', 'grid', 'html', 'latex', 'plain', 'simple', 'tsv', 'json']),
              help="The style used to display a grid. (initially \"simple\")")
@click.option("-u", "--url", "infrabox_url", default=os.environ.get("INFRABOX_URL", None),
              help="Address of the API server.")
@click.option("-c", "--ca-bundle", "ca_bundle", default=os.environ.get('INFRABOX_CA_BUNDLE', None),
              help="The path to a CA_BUNDLE file or directory with certificates of trusted CAs.")
def cli(grid_style, infrabox_url, ca_bundle):
    """
    \f
    :type grid_style: str
    :param grid_style: a tabulate grid style name
    :type infrabox_url: str
    :param infrabox_url: Address of the API server.
    :type ca_bundle: str
    :param ca_bundle: the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
    """

    if grid_style is not None:
        CLI_SETTINGS.grid_style = grid_style
    if infrabox_url:
        CLI_SETTINGS.infrabox_url = infrabox_url
    if ca_bundle:
        CLI_SETTINGS.ca_bundle = ca_bundle


# Adding the commands to the cli
for command in CLI_COMMAND_LIST:
    cli.add_command(command)


def run_cli(args=None, prog_name=None):
    """
    Runs the cli / Catches exceptions.
    :type args: list
    :param args: the arguments for the command line parser
    :type prog_name: str
    :param prog_name: the program's name
    :rtype: int
    :return the exit code
    """
    try:
        ret = 0
        if args is not None:
            cli(args, prog_name=prog_name)
        else:
            cli(prog_name=prog_name)

    except (InfraBoxAPIException, ValidationError) as e:
        logger.error(e, raise_exception=False)
        ret = 1
    except LoggerError:
        ret = 1
    except Exception:
        logger.exception()
        ret = 1
    finally:
        return ret
