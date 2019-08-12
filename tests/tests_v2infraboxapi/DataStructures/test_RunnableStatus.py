import unittest

from v2infraboxapi import RunnableStatus as RS


class TestRunnableStatus(unittest.TestCase):
    def test_comp(self):
        # This test is mostly here to make sure that enumerable comparison works fine in python 2 and 3
        statuses = [RS.RUNNING, RS.QUEUED, RS.KILLED, RS.ERROR, RS.FAILURE, RS.UNSTABLE, RS.SCHEDULED, RS.SKIPPED,
                    RS.OK, RS.FINISHED]
        n = len(statuses)
        for i in range(n):
            for j in range(n):
                if i < j:
                    self.assertLess(statuses[i], statuses[j])
                elif i == j:
                    self.assertEqual(statuses[i], statuses[j])
                else:
                    self.assertGreater(statuses[i], statuses[j])
