from .build import build
from .clear_cache import clear_cache
from .collaborator import collaborator
from .complete import complete_command
from .cronjob import cronjob
from .env_information import get_env_information
from .history import history
from .job import job
from .local import local
from .login import login
from .logout import logout
from .project import project
from .secret import secret
from .ssh_key import ssh_key
from .token import token
from .user_information import get_user_information
from .version import version, CLI_VERSION
from .install import install

CLI_COMMAND_LIST = [login, logout, project, get_user_information, secret, ssh_key, collaborator, token, cronjob, build,
                    job, clear_cache, get_env_information, local, version, history, complete_command, install]
