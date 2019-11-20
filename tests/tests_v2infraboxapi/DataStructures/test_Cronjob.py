import unittest

from v2infraboxapi import Cronjob


class TestCronjob(unittest.TestCase):
    def test_Arrayable(self):
        # This test is mostly here to make sure that attribute conversion works
        cronjob = Cronjob("cronjob_id", "name", "min", "hour", "month", "dow", "dom", "sha", "file")

        # This should not raise an exception
        cronjob.to_string_array(*[attr for attr in cronjob.__dict__ if not callable(cronjob.__dict__[attr])])
