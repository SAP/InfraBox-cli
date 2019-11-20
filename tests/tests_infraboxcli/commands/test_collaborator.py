# import json
# import unittest
# import infraboxcli
# from tests import *
#
#
# class TestCollaborator(unittest.TestCase):
#     def test_add_collaborator(self):
#         # Requires tests: create_delete_project
#         login_as_admin()
#         infraboxcli.CLI_SETTINGS.get_api().create_account("user", "user@user.com", "user", "user")
#         run_cli(["project", "delete", "-n", "TestProjCollab"])
#         run_cli(["project", "create", "-n", "TestProjCollab", "-pub", "-t", "upload"])
#
#         # Test add developer
#         with captured_output() as out:
#             run_cli(["collab", "add", "-u", "user", "-n", "TestProjCollab"])
#             self.assertEqual(out.getvalue().strip(), "Collaborator added successfully.")
#
#         run_cli(["project", "delete", "-n", "TestProjCollab"])
#
#     def test_list_change_role_remove(self):
#         # Requires tests: add_collaborator
#         login_as_admin()
#         infraboxcli.CLI_SETTINGS.get_api().create_account("user", "user@user.com", "user", "user")
#         run_cli(["project", "delete", "-n", "TestProjCollab2"])
#         run_cli(["project", "create", "-n", "TestProjCollab2", "-pub", "-t", "upload"])
#         run_cli(["collab", "add", "-u", "user", "-n", "TestProj"])
#
#         # Test list
#         with captured_output() as out:
#             run_cli(["-s", "json", "collab", "list", "-n", "TestProjCollab2"])
#             output = out.getvalue().strip()
#             self.assertIn("Owner", output)
#             self.assertIn("Developer", output)
#             self.assertEqual(len(json.loads(output)), 2)
#
#         for line in json.loads(output):
#             if line["Role"] == "Developer":
#                 user_id = line["id"]
#                 break
#         else:
#             raise Exception("User id not found")
#
#         # Test change role administrator
#         with captured_output() as out:
#             run_cli(["project", "chg-role", "-n", "TestProjCollab2", "-u", user_id, "-a"])
#             self.assertEqual(out.getvalue().strip(), "Role changed successfully.")
#         with captured_output() as out:
#             run_cli(["collab", "list", "-n", "TestProjCollab2"])
#             output = out.getvalue().strip()
#             self.assertIn("Owner", output)
#             self.assertIn("Administrator", output)
#
#         # Test remove
#         with captured_output() as out:
#             run_cli(["project", "remove", "-n", "TestProjCollab2", "-u", user_id])
#             self.assertEqual(out.getvalue().strip(), "Collaborator removed successfully.")
#             self.assertEqual(run_cli(["project", "remove", "-n", "TestProjCollab2", "-u", user_id]), 1)
#
#         run_cli(["project", "delete", "-n", "TestProjCollab2"])
