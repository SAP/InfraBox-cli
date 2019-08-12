import json
import os
import shutil
import unittest

from tests import *


class TestBuild(unittest.TestCase):
    def test_build(self):
        # Requires tests: create_delete_project
        login_as_admin()
        run_cli(["project", "delete", "-n", "TestProjBuild"])
        run_cli(["project", "create", "-n", "TestProjBuild", "-pub", "-t", "upload"])

        # We need to upload some code first
        cwd = os.getcwd()
        if os.path.isdir(".test_build"):
            shutil.rmtree(".test_build", ignore_errors=True)
        os.makedirs(".test_build")
        os.chdir(".test_build")
        run_cli(["local", "init"])
        # Getting the project's id
        with captured_output() as out:
            run_cli(["-s", "json", "project", "from", "-n", "TestProjBuild"])
            output = json.loads(out.getvalue().strip())
            project_id = output[0]["Id"]
        run_cli(["local", "config", "-p", project_id])
        run_cli(["local", "push"])

        # Test list
        with captured_output() as out:
            run_cli(["-s", "json", "build", "list", "-n", "TestProjBuild", "-l"])
        print(out.getvalue().strip())
        print(out.getvalue().strip().split('\n')[-1])
        output = json.loads(out.getvalue().strip().split('\n')[-1])  # No token found printed
        self.assertEqual(len(output), 1)
        build_id = output[0]["Id"]

        # Test from id
        with captured_output() as out:
            run_cli(["build", "from-id", "-n", "TestProjBuild", "-b", build_id])
            self.assertIn(build_id, out.getvalue().strip())

        # # Test upload
        # with captured_output() as out:
        #     run_cli(["build", "upload", "-n", "TestProjBuild", "-b", build_id])
        #     self.assertIn("Upload successful.", out.getvalue().strip())

        # Test abort
        with captured_output() as out:
            run_cli(["build", "abort", "-n", "TestProjBuild", "-b", build_id])
            self.assertIn("Build successfully aborted.", out.getvalue().strip())

        # Test clear cache
        with captured_output() as out:
            run_cli(["build", "clear", "-n", "TestProjBuild", "-b", build_id])
            self.assertIn("Build cache successfully cleared.", out.getvalue().strip())

        # Test restart
        with captured_output() as out:
            run_cli(["build", "restart", "-n", "TestProjBuild", "-b", build_id])
            self.assertIn("Build successfully restarted.", out.getvalue().strip())

        # Clean up
        run_cli(["project", "delete", "-n", "TestProjBuild"])
        os.chdir(cwd)
        shutil.rmtree(".test_build", ignore_errors=True)
