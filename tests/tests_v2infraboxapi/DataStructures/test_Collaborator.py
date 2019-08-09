import unittest

from v2infraboxapi import Collaborator, CollaboratorRole


class TestCollaborator(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        collab = Collaborator("user_id", "username", "name", "github_id", "email", CollaboratorRole.OWNER)

        # This should not raise an exception
        collab.to_string_array(*[attr for attr in collab.__dict__ if not callable(collab.__dict__[attr])])
