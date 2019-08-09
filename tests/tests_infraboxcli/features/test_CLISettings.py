import os
import unittest
from datetime import datetime

from mock import Mock

from infraboxcli import CLISettings, LoggerError
from v2infraboxapi.DataStructures import *


class TestCLISettings(unittest.TestCase):
    def test_clear_cache(self):
        settings = CLISettings()

        # Testing: If cache recent enough: do nothing
        settings.cache_timestamp = datetime.now()
        old_cache = settings.cached_builds
        settings.clear_cache()
        self.assertIs(settings.cached_builds, old_cache)

        # Testing: Cache recent enough but force option
        old_cache = settings.cached_builds
        settings.clear_cache(force=True)
        self.assertIsNot(settings.cached_builds, old_cache)

        # Testing: Cache too old
        old_cache = settings.cached_builds
        settings.cache_timestamp = datetime.min
        settings.clear_cache()
        self.assertIsNot(settings.cached_builds, old_cache)

    def test_clear_history(self):
        settings = CLISettings()
        p_str, b_str, j_str = ["project_id", "build_id", "job_id"]
        p = settings.id_history[p_str]
        b = settings.id_history[b_str]
        j = settings.id_history[j_str]

        # Clearing one type at a time
        # Project
        settings.clear_history([p_str])
        self.assertIsNot(p, settings.id_history[p_str])
        p = settings.id_history[p_str]
        self.assertIs(b, settings.id_history[b_str])
        self.assertIs(j, settings.id_history[j_str])

        # Build
        settings.clear_history([b_str])
        self.assertIsNot(b, settings.id_history[b_str])
        b = settings.id_history[b_str]
        self.assertIs(p, settings.id_history[p_str])
        self.assertIs(j, settings.id_history[j_str])

        # Job
        settings.clear_history([j_str])
        self.assertIsNot(j, settings.id_history[j_str])
        j = settings.id_history[j_str]
        self.assertIs(p, settings.id_history[p_str])
        self.assertIs(b, settings.id_history[b_str])

        # All at once
        settings.clear_history([p_str, b_str, j_str])
        self.assertIsNot(p, settings.id_history[p_str])
        self.assertIsNot(b, settings.id_history[b_str])
        self.assertIsNot(j, settings.id_history[j_str])

        # Unknown key
        with self.assertRaises(KeyError):
            settings.clear_history([None])

    def test_known_project_names(self):
        settings = CLISettings()
        old_names = settings.known_project_names
        settings.clear_known_project_names()
        self.assertIsNot(old_names, settings.known_project_names)

    def test_delete(self):
        CLISettings._SAVE_PATH = ".test_cli_settings_tmp"

        with open(CLISettings._SAVE_PATH, "w"):
            pass
        CLISettings().delete()
        self.assertFalse(os.path.isfile(CLISettings._SAVE_PATH))

    def test_ca_bundle_setter(self):
        settings = CLISettings()
        path = ".test_cli_settings_ca_bundle_tmp"

        # No file
        if os.path.isfile(path):
            os.remove(path)
        with self.assertRaises(LoggerError):
            settings.ca_bundle = path

        # File
        with open(path, "w"):
            pass
        settings.ca_bundle = path
        self.assertEqual(settings.ca_bundle, path)
        os.remove(path)

    def test_add_build_to_cache(self):
        settings = CLISettings()

        # Check empty cache
        self.assertEqual(settings.cached_builds, dict())

        # Add
        build = Mock(spec=Build, **{"id": "my_id"})
        settings.add_build_to_cache(build)
        self.assertEqual(settings.cached_builds, {build.id: build})

        # Add another
        build2 = Mock(spec=Build, **{"id": "my_id2"})
        settings.add_build_to_cache(build2)
        self.assertEqual(settings.cached_builds, {build.id: build, build2.id: build2})

    def test_get_build_from_cache(self):
        settings = CLISettings()
        build = Mock(spec=Build, **{"id": "my_id"})
        settings.cached_builds = {build.id: build}
        self.assertIsNotNone(settings.get_build_from_cache("my_id"))

    def test_json(self):
        # Requires tests: delete
        settings = CLISettings()
        settings.cached_builds = {}
        settings.cache_timestamp = datetime(2019, 7, 11, 7, 12)
        settings.id_env = {"project_id": 1, "build_id": 2, "job_id": 3}
        settings.id_history = {"project_id": {1}, "build_id": {2}, "job_id": {3}}
        settings.known_project_names = {"abc": 1}
        settings._ca_bundle = ".test_cli_settings_ca_bundle_tmp"
        settings.infrabox_url = "url"
        settings.grid_style = "style"

        # Making CA_BUNDLE file
        with open(settings._ca_bundle, "w"):
            pass

        # Testing to_json gives different results based on attr
        self.assertNotEqual(settings.to_json(), CLISettings().to_json())

        # Testing that to -> from json gives back the data
        json_dict = settings.to_json()
        self.assertNotEqual(json_dict, dict())
        settings2 = CLISettings.from_json(json_dict)

        for attr in settings.__dict__:
            if not callable(settings.__dict__[attr]):
                self.assertEqual(settings.__dict__[attr], settings2.__dict__[attr])

        # Removing temp file
        os.remove(settings._ca_bundle)
        settings.delete()

    def test_save(self):
        # Requires tests: delete/json
        CLISettings._SAVE_PATH = ".test_cli_settings_path_tmp"

        settings = CLISettings()
        settings.cached_builds = {}
        settings.cache_timestamp = datetime(2019, 7, 11, 7, 12)
        settings.id_env = {"project_id": 1, "build_id": 2, "job_id": 3}
        settings.id_history = {"project_id": {1}, "build_id": {2}, "job_id": {3}}
        settings.known_project_names = {"abc": 1}
        settings._ca_bundle = ".test_cli_settings_ca_bundle_tmp"
        settings.infrabox_url = "url"
        settings.grid_style = "style"

        # Testing parameter for save
        settings.save()
        with open(CLISettings._SAVE_PATH, "r") as f:
            string_file = f.readlines()
        settings.delete()

        settings.save(save_env_settings=True)
        with open(CLISettings._SAVE_PATH, "r") as f:
            string_file_full = f.readlines()
        settings.delete()

        self.assertNotEqual(string_file, string_file_full)

    def test_load(self):
        # Requires tests: save
        # Requires tests: delete/json
        CLISettings._SAVE_PATH = ".test_cli_settings_path_load_tmp"

        settings = CLISettings()
        settings.cached_builds = {}
        settings.cache_timestamp = datetime(2019, 7, 11, 7, 12)
        settings.id_env = {"project_id": 1, "build_id": 2, "job_id": 3}
        settings.id_history = {"project_id": {1}, "build_id": {2}, "job_id": {3}}
        settings.known_project_names = {"abc": 1}
        settings._ca_bundle = ".test_cli_settings_ca_bundle_tmp"
        settings.infrabox_url = "url"
        settings.grid_style = "style"

        # Making CA_BUNDLE file
        with open(settings._ca_bundle, "w"):
            pass

        # Testing loading
        settings.save(save_env_settings=True)
        settings2 = CLISettings.load()

        for attr in settings.__dict__:
            if not callable(settings.__dict__[attr]):
                self.assertEqual(settings.__dict__[attr], settings2.__dict__[attr])

        os.remove(settings._ca_bundle)
        settings2.delete()

    def test_get_from_env(self):
        # Requires: clear history
        settings = CLISettings()

        # Unknown key
        settings.id_env = {"project_id": None, "build_id": None, "job_id": None}
        self.assertEqual(settings.get_from_env("value", "__key__"), "value")

        # Testing known keys and no overlap when saving
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            settings.id_env = {"project_id": None, "build_id": None, "job_id": None}
            settings.clear_history(keys)
            settings.get_from_env("value", key)

            for key2 in keys:
                if key == key2:
                    self.assertEqual(settings.id_env[key2], "value")
                    # Also check history
                    self.assertTrue("value" in settings.id_history[key2])
                else:
                    self.assertEqual(settings.id_env[key2], None)
                    # Also check history
                    self.assertFalse("value" in settings.id_history[key2])

        # Testing that we get the right value back
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            settings.id_env = {"project_id": "project_id" * 2,
                               "build_id": "build_id" * 2,
                               "job_id": "job_id" * 2}
            self.assertEqual(key * 2, settings.get_from_env(None, key))

        # Testing error raising if missing value
        settings.id_env = {"project_id": None, "build_id": None, "job_id": None}
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            with self.assertRaises(LoggerError):
                settings.get_from_env(None, key, raise_exception=True)
            self.assertEqual(None, settings.get_from_env(None, key, raise_exception=False))

    def test_completion_from_history(self):
        settings = CLISettings()
        settings.id_history = {"project_id": {"project_id", "_project_id"},
                               "build_id": {"build_id", "_build_id"},
                               "job_id": {"job_id", "_job_id"}
                               }

        # Testing completion failure
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            self.assertEqual([], settings.completion_from_history("__garbage", key))

        # Testing completion
        keys = ["project_id", "build_id", "job_id"]
        for key in keys:
            self.assertEqual([key], settings.completion_from_history(key[:2], key))
            self.assertEqual(settings.id_history[key], set(settings.completion_from_history("", key)))
