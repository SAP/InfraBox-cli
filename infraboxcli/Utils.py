import appdirs
from lockfile import locked as orig_locked, LockTimeout
import os
import infraboxcli

CLI_DATA_DIR = appdirs.user_data_dir("InfraBoxCLI")


def locked(lockfile_path):
    """
    Decorator which acquires a filelock and deletes it if it times out.
    """

    def wrap(f):
        def wrapped(*args, **kwargs):
            try:
                return orig_locked(lockfile_path, timeout=30)(f)(*args, **kwargs)
            except LockTimeout:
                infraboxcli.logger.error("Timeout: on lockfile: " + lockfile_path, raise_exception=False)
                if os.path.isfile(lockfile_path + ".lock"):
                    os.remove(lockfile_path + ".lock")
                    infraboxcli.logger.warn("Lock file deleted: " + lockfile_path)
                    infraboxcli.logger.warn("Please try again.")
                infraboxcli.logger.error()

        return wrapped
    return wrap


class InfraBoxCLIException(Exception):
    pass
