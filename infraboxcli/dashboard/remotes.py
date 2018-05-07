from infraboxcli.dashboard import external
from infraboxcli.log import logger


def list_remotes(args):
    if args.verbose:
        remotes = external.get_all_remotes()

        msg = ': '
        msg += '\n: '.join(remotes)
        logger.info('Remotes:')
        logger.log(msg, print_header=False)
