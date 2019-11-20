import unittest

import click
from mock import patch, Mock

from infraboxcli import MutuallyExclusiveOption, LoggerError, add_project_id_option


class MyException(Exception):
    pass


class TestClickUtils(unittest.TestCase):
    def test_MutuallyExclusiveOption(self):
        @click.command()
        @click.option("--arg1", cls=MutuallyExclusiveOption, mutually_exclusive=["arg2"])
        @click.option("--arg2", cls=MutuallyExclusiveOption, mutually_exclusive=["arg1"])
        def command(arg1, arg2):
            self.assertTrue(arg1 == "val" or arg2 == "val")
            raise MyException("Got in")

        # Testing one arg
        with self.assertRaises(MyException):
            command(["--arg1", "val"])
        with self.assertRaises(MyException):
            command(["--arg2", "val"])

        # Testing two args
        with self.assertRaises(SystemExit) as e:
            command(["--arg1", "val", "--arg2", "val"])
        self.assertEqual(e.exception.code, 2)

    def test_add_project_id_option(self):
        with patch("infraboxcli.CLI_SETTINGS") as settings:
            # ---------------------------------------------
            # Testing arg numbers/config
            # ---------------------------------------------
            @click.command()
            @add_project_id_option
            def command(project_id):
                self.assertEqual(project_id, expected_value)
                raise MyException("Got in")

            expected_value = "project_id"

            # Testing project_id only
            settings.get_from_env.return_value = "project_id"
            with self.assertRaises(MyException):
                command(["-p", "project_id"])

            # Testing known name only
            settings.known_project_names.get.return_value = "project_id"
            with self.assertRaises(MyException):
                command(["-n", "project_id"])
            self.assertEqual(settings.get_api.call_count, 0)

            # Testing unknown name only
            settings.known_project_names.get.return_value = None
            settings.get_api.reset_mock()
            # Extra mocking
            project_name_mock = Mock(**{"id": "project_id"})
            api_mock = Mock()
            api_mock.get_project_by_name.return_value = project_name_mock
            settings.get_api.return_value = api_mock

            with self.assertRaises(MyException):
                command(["-n", "project_id"])
            self.assertEqual(settings.get_api.call_count, 1)

            # Testing two options at a time
            with self.assertRaises(LoggerError):
                command(["-n", "project_id", "-p", "project_id"])
