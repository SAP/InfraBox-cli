# import json
# import unittest
#
# from tests import *
#
#
# class TestCronjob(unittest.TestCase):
#     def test_create_list_delete_cronjob(self):
#         # Requires tests: create_delete_project
#         login_as_admin()
#         run_cli(["project", "delete", "-n", "TestProjCronjob"])
#         run_cli(["project", "create", "-n", "TestProjCronjob", "-pub", "-t", "upload"])
#
#         # Test create
#         with captured_output() as out:
#             run_cli(
#                 ["cronjob", "create", "-cn", "MyCronJob", "-min", "-", "-h", "-", "-dm", "-", "-m", "-", "-dw", "-",
#                  "-s", "sha", "-f", "infrabox.json", "-n", "TestProjCronjob"])
#             self.assertIn("Cronjob created successfully.", out.getvalue().strip())
#
#         # Test list
#         with captured_output() as out:
#             run_cli(["-s", "json", "cronjob", "list", "-n", "TestProjCronjob"])
#             output = json.load(out.getvalue().strip())
#             expected = {"Name": "MyCronJob", "Minute": "-", "Hour": "-", "Day of month": "-", "Month": "-",
#                         "Day of week": "-", "Sha": "sha", "InfraBox File": "infrabox.json"}
#             self.assertEqual(len(output), 1)
#             for key in expected:
#                 self.assertEqual(output[0][key], expected[key])
#
#         # Test delete
#         with captured_output() as out:
#             run_cli(["cronjob", "delete", "-n", "TestProjCronjob", "-c", output[0]["Id"]])
#             self.assertEqual(out.getvalue().strip(), "Project deleted successfully.")
#             self.assertEqual(run_cli(["cronjob", "delete", "-n", "TestProjCronjob", "-c", output[0]["Id"]]), 1)
#
#         run_cli(["project", "delete", "-n", "TestProjCronjob"])
