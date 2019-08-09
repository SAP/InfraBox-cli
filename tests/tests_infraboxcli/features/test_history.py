import unittest

import infraboxcli
from infraboxcli import CLISettings
from infraboxcli.commands import history


class TestHistory(unittest.TestCase):
    def test_save(self):
        CLISettings._SAVE_PATH = ".test_cli_settings_path_tmp"
        infraboxcli.CLI_SETTINGS = infraboxcli.CLI_SETTINGS.load()
        settings = infraboxcli.CLI_SETTINGS

        # Testing the clear option
        settings.id_history = {"project_id": {1}, "build_id": {2}, "job_id": {3}}
        settings.delete()

        # No folder
        with self.assertRaises(SystemExit) as e:
            history(["--clear"])
        self.assertEqual(e.exception.code, 0)

        new_settings = settings.load()
        # Testing if the current settings are cleared
        for key in settings.id_history:
            self.assertEqual(settings.id_history[key], set())

        # Testing if the saved settings are cleared
        self.assertEqual(settings.known_project_names, new_settings.known_project_names)
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            self.assertEqual(settings.id_history[key], new_settings.id_history[key])
        settings.delete()
