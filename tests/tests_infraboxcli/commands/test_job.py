# import json
# import os
# import shutil
# import unittest
#
# from tests import *
#
#
# class TestJob(unittest.TestCase):
#     def test_job(self):
#         # Requires tests: create_delete_project
#         login_as_admin()
#         run_cli(["project", "delete", "-n", "TestProjJob"])
#         run_cli(["project", "create", "-n", "TestProjJob", "-pub", "-t", "upload"])
#
#         # We need to upload some code first
#         cwd = os.getcwd()
#         if os.path.isdir(".test_build"):
#             shutil.rmtree(".test_build", ignore_errors=True)
#         os.makedirs(".test_build")
#         os.chdir(".test_build")
#         run_cli(["local", "init"])
#         # Getting the project's id
#         with captured_output() as out:
#             run_cli(["-s", "json", "project", "from", "-n", "TestProjJob"])
#             output = json.loads(out.getvalue().strip())
#             project_id = output[0]["Id"]
#             run_cli(["local", "config", "-p", project_id])
#             run_cli(["local", "push"])
#         # Getting the build's id
#         with captured_output() as out:
#             run_cli(["-s", "json", "build", "list", "-n", "TestProjJob", "-l"])
#             output = json.loads(out.getvalue().strip().split('\n')[-1])  # No token found printed
#             build_id = output[0]["Id"]
#         # Creating a token
#         run_cli(["token", "create", "-n", "TestProjJob", "-l", "-h", "-s", "-d", "Testing"])
#
#         # Test list normal
#         with captured_output() as out:
#             run_cli(["-s", "json", "job", "list", "-n", "TestProjJob", "-b", build_id])
#             # We split the concatenated json in 2
#             raw = out.getvalue().strip()
#
#         output = json.loads(raw[raw.rfind("\n"):])
#         self.assertGreaterEqual(output, 1)
#         job_id = output[0]["Id"]
#
#         # Test list tree
#         # We just want to check that no exception is being raised
#         ret = run_cli(["job", "list", "-n", "TestProjJob", "-b", build_id, "-t"])
#         self.assertEqual(ret, 0)
#
#         # Test log
#         with captured_output() as out:
#             run_cli(["job", "log", "-n", "TestProjJob", "-j", job_id])
#             self.assertNotEqual("", out.getvalue().strip())
#
#         # Test stats
#         # We just want to check that no exception is being raised
#         ret = run_cli(["job", "stats", "-n", "TestProjJob", "-j", job_id])
#         self.assertEqual(ret, 0)
#
#         # Test from-id
#         with captured_output() as out:
#             run_cli(["-s", "json", "job", "from-id", "-n", "TestProjJob", "-j", job_id])
#             output = out.getvalue().strip()
#             self.assertIn(job_id, output)
#
#         # Test list archives
#         # with captured_output() as out:
#         ret = run_cli(["-s", "json", "job", "list-archives", "-n", "TestProjJob", "-j", job_id])
#         # output = out.getvalue().strip()
#         # self.assertIn("all_archives.tar.gz", output)
#         self.assertEqual(ret, 0)
#
#         # Test download archive
#         # with captured_output() as out:
#         #     run_cli(["-s", "json", "job", "archives", "-n", "TestProjJob", "-j", job_id, "-f", "all_archives.tar.gz"])
#         #     output = out.getvalue().strip()
#         #     self.assertIn("File downloaded successfully.", output)
#         #     self.assertTrue(os.path.isfile("all_archives.tar.gz"))
#         #     os.remove("all_archives.tar.gz")
#
#         # Test clear cache
#         with captured_output() as out:
#             run_cli(["-s", "json", "job", "clear", "-n", "TestProjJob", "-j", job_id])
#             output = out.getvalue().strip()
#             self.assertIn("Job cache cleared successfully.", output)
#
#         # Test restart
#         with captured_output() as out:
#             run_cli(["-s", "json", "job", "restart", "-n", "TestProjJob", "-j", job_id])
#             output = out.getvalue().strip()
#         print(output)
#         self.assertIn("Job restarted successfully.", output)
#
#         # TODO test get testruns; pull
#
#         # Clean up
#         run_cli(["project", "delete", "-n", "TestProjJob"])
#         run_cli(["token", "local-delete", "-n", "TestProjJob", "-l", "-h"])
#         os.chdir(cwd)
#         shutil.rmtree(".test_build", ignore_errors=True)
