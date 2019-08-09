import sys
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from infraboxcli import run_cli

USER_EMAIL = "admin@admin.com"
USER_PASSWORD = "admin"


@contextmanager
def captured_output():
    new_out = StringIO()
    old_out = sys.stdout

    try:
        sys.stdout = new_out
        yield sys.stdout
    finally:
        sys.stdout = old_out


def login_as_admin():
    run_cli(["login", "-e", USER_EMAIL, "-p", USER_PASSWORD])
