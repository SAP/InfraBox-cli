import json
import unittest

from tests import *


class TestSecret(unittest.TestCase):
    def test_create_list_delete_secret(self):
        # Requires tests: create_delete_project
        login_as_admin()
        run_cli(["project", "delete", "-n", "TestProjSecret"])
        run_cli(["project", "create", "-n", "TestProjSecret", "-pub", "-t", "upload"])

        # Test create
        with captured_output() as out:
            run_cli(["secret", "create", "-sn", "SecretName", "-v", "Val", "-n", "TestProjSecret"])
        self.assertIn("Secret created successfully.", out.getvalue().strip())

        # Test list
        with captured_output() as out:
            run_cli(["-s", "json", "secret", "list", "-n", "TestProjSecret"])
            output = json.loads(out.getvalue().strip())
            self.assertEqual(len(output), 1)
            self.assertEqual(output[0]["Name"], "SecretName")

        # Test delete
        with captured_output() as out:
            run_cli(["secret", "delete", "-n", "TestProjSecret", "-s", output[0]["Id"]])
            self.assertIn("Secret deleted successfully.", out.getvalue().strip())
            self.assertEqual(run_cli(["secret", "delete", "-n", "TestProjSecret", "-s", output[0]["Id"]]), 1)

        run_cli(["project", "delete", "-n", "TestProjSecret"])
