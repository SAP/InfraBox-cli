# import json
# import unittest
#
# from tests import *
#
#
# class TestSSHKey(unittest.TestCase):
#     def test_create_list_delete_sshkey(self):
#         # Requires tests: create_delete_secret
#         login_as_admin()
#         run_cli(["project", "delete", "-n", "TestProjSSHKey"])
#         run_cli(["project", "create", "-n", "TestProjSSHKey", "-pub", "-t", "upload"])
#         run_cli(["secret", "create", "-sn", "SecretName", "-v", "Val", "-n", "TestProjSecret"])
#
#         # Test create
#         with captured_output() as out:
#             run_cli(
#                 ["ssh-key", "create", "-kn", "KeyName", "-sn", "SecretName", "-n", "TestProjSSHKey"])
#             self.assertIn("SSH key created successfully.", out.getvalue().strip())
#
#         # Test list
#         with captured_output() as out:
#             run_cli(["-s", "json", "secret", "list", "-n", "TestProjSSHKey"])
#             output = json.loads(out.getvalue().strip())
#             expected = {"Name": "KeyName", "Value": "Val"}
#             self.assertEqual(len(output), 1)
#             for key in expected:
#                 self.assertEqual(output[0][key], expected[key])
#
#         # Test delete
#         with captured_output() as out:
#             run_cli(["ssh-key", "delete", "-n", "TestProjSSHKey", "-s", output[0]["Id"]])
#             self.assertIn("SSH key deleted successfully.", out.getvalue().strip())
#             self.assertEqual(run_cli(["ssh-key", "delete", "-n", "TestProj", "-s", output[0]["Id"]]), 1)
#
#         run_cli(["project", "delete", "-n", "TestProjSSHKey"])
