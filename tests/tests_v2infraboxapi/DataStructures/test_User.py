import unittest

from v2infraboxapi import User


class TestUser(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        user = User("user_id", "username", "name", "github_id", "email")

        # This should not raise an exception
        user.to_string_array(*[attr for attr in user.__dict__ if not callable(user.__dict__[attr])])
