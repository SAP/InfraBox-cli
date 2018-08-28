from infraboxcli.dashboard import local_config
from infraboxcli.log import logger


def list_remotes(args):
    if args.verbose:
        remotes = local_config.get_all_remotes()

        msg = '\n: '.join(remotes)
        logger.info('Remotes:')
        logger.log(msg, print_header=False)
