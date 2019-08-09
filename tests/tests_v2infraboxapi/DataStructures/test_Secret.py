import unittest

from v2infraboxapi import Secret


class TestSecret(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        secret = Secret("secret_id", "name")

        # This should not raise an exception
        secret.to_string_array(*[attr for attr in secret.__dict__ if not callable(secret.__dict__[attr])])
