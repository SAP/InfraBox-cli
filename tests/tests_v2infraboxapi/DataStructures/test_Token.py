import unittest

from v2infraboxapi import Token


class TestToken(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        token = Token("token_id", "desc", True, False)

        # This should not raise an exception
        token.to_string_array(*[attr for attr in token.__dict__ if not callable(token.__dict__[attr])])
