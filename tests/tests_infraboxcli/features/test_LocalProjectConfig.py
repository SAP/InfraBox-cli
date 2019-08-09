import os
import shutil
import unittest

from mock import patch

from infraboxcli import LocalProjectConfig, LoggerError


class MyException(Exception):
    pass


class TestClickUtils(unittest.TestCase):
    def test_infrabox_file_setter(self):
        config = LocalProjectConfig("url", "project_id", False)

        # Testing: setting to None
        self.assertFalse(config._infrabox_file)
        self.assertFalse(config.infrabox_file)
        config.infrabox_file = None
        self.assertIsNone(config._infrabox_file)
        self.assertIsNone(config.infrabox_file)

        # Testing set to missing file
        path = ".test_local_config_tmp"
        if os.path.isfile(path):
            os.remove(path)

        with self.assertRaises(LoggerError):
            config.infrabox_file = path

        # Testing: existing file
        with open(path, "w"):
            pass
        config.infrabox_file = path
        self.assertEqual(config._infrabox_file, os.path.abspath(path))
        self.assertEqual(config.infrabox_file, os.path.abspath(path))

        os.remove(path)

    def test_load(self):
        # Setting up env
        path = ".test_local_config_dir"
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)
        os.chdir(path)

        # Testing: no root found
        prev_path = os.getcwd()
        os.chdir("/")
        with self.assertRaises(LoggerError):
            LocalProjectConfig.load()
        os.chdir(prev_path)

        # Testing: infrabox.json in current dir but no local conf
        with open("infrabox.json", "w"):
            pass

        local_conf_path = LocalProjectConfig._get_local_config_file_path("./")
        if os.path.isfile(local_conf_path):
            os.remove(local_conf_path)

        LocalProjectConfig.load()
        self.assertTrue(os.path.isfile(local_conf_path))
        os.remove(local_conf_path)

        # Testing: existing local conf
        conf = LocalProjectConfig("url", "project_id", "infrabox.json")
        conf.save()
        self.assertEqual(conf.load().__dict__, conf.__dict__)

        # Testing: infrabox file in subdir and existing conf file
        path2 = ".test_local_config_dir2"
        if os.path.isdir(path2):
            shutil.rmtree(path2, ignore_errors=True)
        os.makedirs(path2)
        os.chdir(path2)

        self.assertEqual(conf.load().__dict__, conf.__dict__)
        os.chdir("..")

        os.chdir("..")
        shutil.rmtree(path, ignore_errors=True)

    def test_check_tokens(self):
        config = LocalProjectConfig("url", "project_id", False)

        # Testing no project id
        config.project_id = None
        self.assertFalse(config.check_tokens())

        # Testing: no token found for project id
        config.project_id = "project_id"
        with patch("infraboxcli.CLI_TOKEN_MANAGER.get_token", return_value=None):
            self.assertFalse(config.check_tokens())

        # Testing:  token found for project id
        config.project_id = "project_id"
        with patch("infraboxcli.CLI_TOKEN_MANAGER.get_token", return_value={"token": "val"}):
            self.assertTrue(config.check_tokens())
