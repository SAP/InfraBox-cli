from __future__ import print_function

import sys

import click
from click._bashcomplete import get_choices

import infraboxcli


@click.command(name="complete", hidden=True)
@click.argument("cwords")
@click.argument("cword")
def complete_command(cwords, cword):
    """
    Hidden command used to trigger auto-completion.
    \f
    :type cwords: str
    :param cwords: command line to complete in the format "\n".join(args)
    :type cword: str
    :param cword: str containing the of the word we need to complete
    """
    cwords = [w for w in cwords.split('\n') if w]
    cword = int(cword)
    try:
        incomplete = cwords[cword]
    except IndexError:
        incomplete = ''

    for item in get_choices(infraboxcli.cli, "complete", cwords[1:cword], incomplete):
        click.utils.echo(item[0], file=sys.stdout)
