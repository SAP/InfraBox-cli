import json
import os
import shutil
import unittest

from tests import *


class TestProject(unittest.TestCase):
    def test_create_delete_project(self):
        # Requires tests: login
        login_as_admin()
        run_cli(["project", "delete", "-n", "TestProj"])
        run_cli(["project", "delete", "-n", "TestProj2"])
        run_cli(["project", "delete", "-n", "TestProj3"])

        # Test create public upload
        with captured_output() as out:
            run_cli(["project", "create", "-n", "TestProj", "-pub", "-t", "upload"])
            self.assertIn("Project created successfully.", out.getvalue().strip())

        # Test create gerrit
        with captured_output() as out:
            run_cli(["project", "create", "-n", "TestProj2", "-t", "gerrit"])
            self.assertIn("Project created successfully.", out.getvalue().strip())

        # Test create github
        # with captured_output() as out:
        #     run_cli(["project", "create", "-n", "TestProj3", "-t", "github", "-repo", "user/repo"])
        #     # TODO fix this test. But it would require giving it access to a github account
        #     self.assertIn("Server Error", out.getvalue().strip())

        # Test create existing
        ret = run_cli(["project", "create", "-n", "TestProj", "-pub", "-t", "upload"])
        self.assertEqual(ret, 1)

        # Test delete
        with captured_output() as out:
            run_cli(["project", "delete", "-n", "TestProj"])
            self.assertIn("Project deleted successfully.", out.getvalue().strip())
            self.assertEqual(run_cli(["project", "delete", "-n", "TestProj"]), 1)

            # Test list
            with captured_output() as out:
                run_cli(["project", "list"])
                output = out.getvalue().strip()
                self.assertIn("TestProj2", output)

        run_cli(["project", "delete", "-n", "TestProj2"])
        # run_cli(["project", "delete", "-n", "TestProj3"])

        # Test that the project name history has been cleared and does not offer the wrong project_id when a project
        # with the same name is created
        run_cli(["project", "create", "-n", "TestProj"])
        ret = run_cli(["project", "delete", "-n", "TestProj"])
        self.assertEqual(ret, 0)

    # def test_change_visibility(self):
    #     # Requires tests: create_delete_project
    #     login_as_admin()
    #     run_cli(["project", "delete", "-n", "TestProj4"])
    #     run_cli(["project", "create", "-n", "TestProj4", "-pub", "-t", "upload"])
    #
    #     # Test change visibility
    #     with captured_output() as out:
    #         run_cli(["project", "chg-visib", "-n", "TestProj4"])
    #         self.assertIn("Visibility changed successfully.", out.getvalue().strip())
    #     with captured_output() as out:
    #         run_cli(["project", "list"])
    #         output = out.getvalue().strip()
    #         self.assertIn("private", output)
    #
    #     run_cli(["project", "delete", "-n", "TestProj4"])

    def test_trigger(self):
        # Requires tests: create_delete_project
        login_as_admin()
        run_cli(["project", "delete", "-n", "TestProjTrigger"])
        run_cli(["project", "create", "-n", "TestProjTrigger", "-pub", "-t", "upload"])

        # We need to upload some code first
        cwd = os.getcwd()
        if os.path.isdir(".test_trigger"):
            shutil.rmtree(".test_trigger", ignore_errors=True)
        os.makedirs(".test_trigger")
        os.chdir(".test_trigger")
        run_cli(["local", "init"])
        # Getting the project's id
        with captured_output() as out:
            run_cli(["-s", "json", "project", "from", "-n", "TestProjTrigger"])
            output = json.loads(out.getvalue().strip())
            project_id = output[0]["Id"]
        run_cli(["local", "config", "-p", project_id])
        run_cli(["local", "push"])

        # Test trigger
        with captured_output() as out:
            run_cli(["project", "trigger", "-n", "TestProjTrigger", "-b", "Test", "-w"])
            self.assertIn("Waiting for the build to finish...", out.getvalue().strip())
            self.assertIn("Build finished with status: ", out.getvalue().strip())

        # Clean up
        run_cli(["project", "delete", "-n", "TestProjTrigger"])
        os.chdir(cwd)
        shutil.rmtree(".test_trigger", ignore_errors=True)
