from infraboxcli.log import logger
from pyinfrabox.utils import get_remote_url
from infraboxcli.dashboard import local_config


def save_user_token(url, cookies_dict):
    config = local_config.get_config()
    if config is None:
        config = {}

    config.setdefault('remotes', {})

    is_new_remote_or_null = False
    remote_url = get_remote_url(url)
    if remote_url not in config['remotes'] \
            or config['remotes'][remote_url] is None:
        is_new_remote_or_null = True

    # Decide what are we going to do if user entered invalid username or password:
    # either use `current_user_token` if it exists or raise an error
    allow_login_if_current_user_token_is_set = False

    user_token = None
    if 'token' not in cookies_dict:
        if is_new_remote_or_null or not allow_login_if_current_user_token_is_set:
            logger.error('Unauthorized: invalid username and/or password.')
            exit(1)
        else:
            user_token = config['remotes'][remote_url]['current_user_token']
    else:
        user_token = cookies_dict['token']

    config['current_remote'] = remote_url
    config['remotes'].setdefault(remote_url, {})
    config['remotes'][remote_url]['current_user_token'] = user_token

    local_config.save_config(config)
    logger.info('Logged in successfully.')


def get_current_user_token():
    try:
        config = local_config.get_config()

        current_remote = config['current_remote']
        if not current_remote:
            raise

        current_user_token = config['remotes'][current_remote]['current_user_token']
        if current_user_token is None or not current_user_token:
            raise

        return current_user_token
    except:
        logger.error('Could not load current user token. Please, log in.')
        exit(1)


def delete_current_user_token(args=None):
    try:
        config = local_config.get_config()

        current_remote = config['current_remote']
        if not current_remote:
            raise

        if not config['remotes'][current_remote]['current_user_token']:
            return False

        config['remotes'][current_remote]['current_user_token'] = ""
        local_config.save_config(config)

        return True
    except:
        return False
