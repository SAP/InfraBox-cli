import json
import unittest

from tests import *


class TestToken(unittest.TestCase):
    def test_create_list_delete_token(self):
        # Requires tests: create_delete_project
        login_as_admin()
        run_cli(["project", "delete", "-n", "TestProjToken"])
        run_cli(["project", "create", "-n", "TestProjToken", "-pub", "-t", "upload"])

        # Getting the project id


        # Test create
        with captured_output() as out:
            run_cli(
                ["token", "create", "-d", "Description", "-h", "-l", "-s", "-n", "TestProjToken"])
            self.assertNotEqual(out.getvalue().strip(), "")

        # Test list
        with captured_output() as out:
            run_cli(["-s", "json", "token", "list", "-n", "TestProjToken"])
        print(out.getvalue().strip())
        output = json.loads(out.getvalue().strip())
        expected = {"Description": "Description", "Allows to push": "True", "Allows to pull": "True"}
        self.assertEqual(len(output), 1)
        for key in expected:
            self.assertEqual(output[0][key], expected[key])

        # Test delete
        with captured_output() as out:
            run_cli(["token", "delete", "-n", "TestProjToken", "-t", output[0]["Id"]])
            self.assertIn("Token deleted successfully.", out.getvalue().strip())
            self.assertEqual(run_cli(["secret", "delete", "-n", "TestProj", "-s", output[0]["Id"]]), 1)

        run_cli(["project", "delete", "-n", "TestProjToken"])
