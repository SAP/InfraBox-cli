import unittest

from v2infraboxapi import Testrun, RunnableStatus


class TestTestrun(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        run = Testrun(RunnableStatus.RUNNING, "name", "suite", "1000", "2000-01-01 00:00:00", "stack", "message")

        # This should not raise an exception
        run.to_string_array(*[attr for attr in run.__dict__ if not callable(run.__dict__[attr])])
