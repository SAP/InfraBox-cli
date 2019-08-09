import os
import unittest

import infraboxcli
from infraboxcli import CLISettings
from infraboxcli.commands import get_env_information


class TestEnvInformation(unittest.TestCase):
    def test_save(self):
        CLISettings._SAVE_PATH = ".test_cli_settings_path_tmp"
        prev_settings = CLISettings()
        prev_settings.delete()

        # Testing the env settings changes
        infraboxcli.CLI_SETTINGS = infraboxcli.CLI_SETTINGS.load()
        settings = infraboxcli.CLI_SETTINGS
        settings._ca_bundle = ".test_cli_settings_ca_bundle_tmp"
        settings.infrabox_url = "url"
        settings.grid_style = "json"

        # Making CA_BUNDLE file
        with open(settings._ca_bundle, "w"):
            pass

        with self.assertRaises(SystemExit) as e:
            get_env_information(["-s"])
        self.assertEqual(e.exception.code, 0)

        new_settings = infraboxcli.CLI_SETTINGS.load()

        # Checking equal to current
        self.assertEqual(settings._ca_bundle, str(new_settings._ca_bundle))
        self.assertEqual(settings.infrabox_url, str(new_settings.infrabox_url))
        self.assertEqual(settings.grid_style, str(new_settings.grid_style))

        # Checking not equal to prev
        self.assertNotEqual(prev_settings._ca_bundle, str(new_settings._ca_bundle))
        self.assertNotEqual(prev_settings.infrabox_url, str(new_settings.infrabox_url))
        self.assertNotEqual(prev_settings.grid_style, str(new_settings.grid_style))
        os.remove(settings._ca_bundle)

        prev_settings.delete()
