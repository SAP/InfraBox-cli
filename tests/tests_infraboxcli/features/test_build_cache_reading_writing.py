import unittest

from mock import patch, Mock

import infraboxcli
from infraboxcli.commands.build import build_from_id, list_builds
from infraboxcli.commands.job import list_jobs
from v2infraboxapi import Build


class MyException(Exception):
    pass


class TestBuildCache(unittest.TestCase):
    def test_build_writing_build_from_id(self):
        infraboxcli.CLISettings._SAVE_PATH = ".test_save_path_tmp"
        infraboxcli.CLI_SETTINGS = infraboxcli.CLISettings.load()

        settings = infraboxcli.CLI_SETTINGS

        with patch("infraboxcli.CLI_SETTINGS.get_build_from_cache") as cache:
            with patch("infraboxcli.CLI_SETTINGS.save"):
                with patch("infraboxcli.CLI_SETTINGS.get_api"):
                    # Testing build in cache
                    cached_build = Mock()
                    cached_build.to_string_array = lambda *args, **kwargs: []
                    cache.return_value = cached_build

                    with self.assertRaises(SystemExit) as e:
                        build_from_id(["-p", "p", "-b", "b"])
                    self.assertEqual(e.exception.code, 0)
                    settings.get_api.assert_not_called()

    def test_build_writing_list_builds(self):
        infraboxcli.CLISettings._SAVE_PATH = ".test_save_path_build_cache_tmp"
        infraboxcli.CLI_SETTINGS = infraboxcli.CLISettings.load()

        settings = infraboxcli.CLI_SETTINGS
        settings.clear_history(["build_id"])

        with patch("v2infraboxapi.DataStructures.Build.list_last_builds") as get_builds:
            with patch("infraboxcli.CLI_SETTINGS.save"):
                # Testing adding builds to cache
                build = Mock()
                build.to_string_array = lambda *args, **kwargs: []
                build.id = "build_id"
                get_builds.return_value = [build]

                with self.assertRaises(SystemExit) as e:
                    list_builds(["-p", "p", "--long"])
                self.assertEqual(e.exception.code, 0)
                self.assertTrue("build_id" in settings.id_history["build_id"])

    def test_build_reading_list_jobs(self):
        # Requires tests: clear_cache
        infraboxcli.CLISettings._SAVE_PATH = ".test_save_path_build_cache_tmp"
        infraboxcli.CLI_SETTINGS = infraboxcli.CLISettings.load()

        settings = infraboxcli.CLI_SETTINGS
        settings.clear_cache(True)

        build = Mock(spec=Build, id="build_id", jobs=[], commit=None)
        build.to_string_array = lambda *args, **kwargs: []
        settings.add_build_to_cache(build)

        with patch("infraboxcli.CLI_SETTINGS.save"):
            with patch("infraboxcli.CLI_SETTINGS.get_api") as api:
                # Testing reading builds from cache

                with self.assertRaises(SystemExit) as e:
                    list_jobs(["-p", "project_id", "-b", "build_id"])
                self.assertEqual(e.exception.code, 0)
                api.assert_not_called()

                # Testing ignoring build from cache
                api.side_effect = MyException
                with self.assertRaises(MyException):
                    list_jobs(["-p", "project_id", "-b", "build_id", "-i"])
