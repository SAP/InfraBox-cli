import os
import shutil
import unittest

from infraboxcli import CLITokenManager
from v2infraboxapi.TokenManager import TokenKind


class TestCLITokenManager(unittest.TestCase):
    def test_constructor_login(self):
        path = CLITokenManager._LOGIN_TOKEN_PATH = ".test_login_token_tmp"

        # Testing: no file
        if os.path.isfile(path):
            shutil.rmtree(path, ignore_errors=True)
        manager = CLITokenManager()
        self.assertIsNone(manager._login_token)

        # Testing: file
        with open(path, "w") as f:
            f.write("token\nline")
        manager = CLITokenManager()
        self.assertEqual(manager._login_token, {"token": "tokenline"})

        os.remove(path)

    def test_login(self):
        path = CLITokenManager._LOGIN_TOKEN_PATH = ".test_login_token_tmp"

        # Testing: logging in
        CLITokenManager().login("tokenline")
        self.assertTrue(os.path.isfile(path))
        os.remove(path)

    def test_logout(self):
        path = CLITokenManager._LOGIN_TOKEN_PATH = ".test_login_token_tmp"

        # Testing: logging out no file
        if os.path.isfile(path):
            shutil.rmtree(path, ignore_errors=True)

        self.assertFalse(CLITokenManager().logout())
        self.assertFalse(os.path.isfile(path))

        # Testing: logging out with file
        with open(path, "w") as f:
            f.write("token\nline")
        self.assertTrue(CLITokenManager().logout())
        self.assertFalse(os.path.isfile(path))

    def test_save_token(self):
        path = CLITokenManager._PROJECT_TOKEN_FOLDER = ".test_token_folder_tmp"

        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)

        manager = CLITokenManager()
        project_id = "project_id"
        token = "tokenline"

        # Testing: no right
        manager.save_token(project_id, token, pull=False, push=False)
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, False)))

        # Testing: pull right
        manager.save_token(project_id, token, pull=True, push=False)
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, False)))
        os.remove(manager._project_id_to_token_path(project_id, True))

        # Testing: push right
        manager.save_token(project_id, token, pull=False, push=True)
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, False)))
        os.remove(manager._project_id_to_token_path(project_id, False))

        # Testing: both rights
        manager.save_token(project_id, token, pull=True, push=True)
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, False)))
        os.remove(manager._project_id_to_token_path(project_id, True))
        os.remove(manager._project_id_to_token_path(project_id, False))

        os.removedirs(path)

    def test_delete_token(self):
        # Requires tests: save
        path = CLITokenManager._PROJECT_TOKEN_FOLDER = ".test_token_folder_tmp"

        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)

        manager = CLITokenManager()
        project_id = "project_id"
        token = "tokenline"

        # Testing: no right
        manager.save_token(project_id, token, pull=True, push=True)
        manager.delete_token(project_id, pull=False, push=False)
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, False)))

        # Testing: pull right
        manager.save_token(project_id, token, pull=True, push=True)
        manager.delete_token(project_id, pull=True, push=False)
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, False)))

        # Testing: push right
        manager.save_token(project_id, token, pull=True, push=True)
        manager.delete_token(project_id, pull=False, push=True)
        self.assertTrue(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, False)))

        # Testing: both rights
        manager.save_token(project_id, token, pull=True, push=True)
        manager.delete_token(project_id, pull=True, push=True)
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, True)))
        self.assertFalse(os.path.isfile(manager._project_id_to_token_path(project_id, False)))

        os.removedirs(path)

    def test_get_token(self):
        # Requires tests: save_token, delete_token
        path = CLITokenManager._PROJECT_TOKEN_FOLDER = ".test_token_folder_tmp"

        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)

        manager = CLITokenManager()
        project_id = "project_id"
        token = "tokenline"

        # Testing: getting User token but no token
        manager._login_token = None
        self.assertIsNone(manager.get_token(TokenKind.USER))

        # Testing: getting User token and token registered
        login_token = manager._login_token = {"token": "login"}
        self.assertIs(manager.get_token(TokenKind.USER), login_token)

        # Testing: getting Pull token but no token
        login_token = manager._login_token = {"token": "login"}
        self.assertIs(manager.get_token(TokenKind.PULL, project_id=project_id), login_token)

        # Testing: getting Pull token and token registered
        manager.save_token(project_id, token, pull=True, push=False)
        self.assertEqual(manager.get_token(TokenKind.PULL, project_id=project_id), {"token": token})
        manager.delete_token(project_id, pull=True, push=False)

        # Testing: getting Push token but no token
        login_token = manager._login_token = {"token": "login"}
        self.assertIs(manager.get_token(TokenKind.PUSH, project_id=project_id), login_token)

        # Testing: getting Pull token and token registered
        manager.save_token(project_id, token, push=True, pull=False)
        self.assertEqual(manager.get_token(TokenKind.PUSH, project_id=project_id), {"token": token})
        manager.delete_token(project_id, push=True, pull=False)

        shutil.rmtree(path, ignore_errors=True)
