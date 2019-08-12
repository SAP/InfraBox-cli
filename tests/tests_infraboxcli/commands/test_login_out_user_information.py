import unittest
from tests import *


class TestLogInOutUserInformation(unittest.TestCase):
    def test_log_in_out_user_information(self):
        # Test login fail
        with captured_output() as out:
            run_cli(["login", "-e", "", "-p", ""])
            self.assertIn("[infrabox] Server Error: Invalid email/password combination", out.getvalue().strip())

        # Test login success
        with captured_output() as out:
            login_as_admin()
            self.assertIn("Login Successful", out.getvalue().strip())

        # Test login success (when already logged in)
        with captured_output() as out:
            login_as_admin()
            self.assertIn("Login Successful", out.getvalue().strip())

        # TODO check that if a different user logs in, the user token gets replaced

        # Test user information
        with captured_output() as out:
            run_cli(["user"])
            self.assertIn(ADMIN_EMAIL, out.getvalue().strip())

        # Test logout
        with captured_output() as out:
            run_cli(["logout"])
            self.assertIn("Successfully logged out", out.getvalue().strip())

        # Test already logged out
        with captured_output() as out:
            run_cli(["logout"])
            self.assertIn("Already logged out", out.getvalue().strip())

        # Test user information fail
        with captured_output() as out:
            ret = run_cli(["user"])
            self.assertEqual(ret, 1)
