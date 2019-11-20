import unittest

from v2infraboxapi import SSHKey


class TestSSHKey(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        key = SSHKey("key_id", "name", "secret_name")

        # This should not raise an exception
        key.to_string_array(*[attr for attr in key.__dict__ if not callable(key.__dict__[attr])])
