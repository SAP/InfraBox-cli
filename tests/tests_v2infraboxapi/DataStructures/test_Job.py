import unittest
from datetime import timedelta

from v2infraboxapi import Job, RunnableStatus


class TestJob(unittest.TestCase):
    def test_json(self):
        # This test is mostly here to make sure that converting to json works in both ways
        job = Job("job_id", "project_id", "job_name", "2000-01-01 00:00:00", "2020-01-01 00:00:00",
                  RunnableStatus.RUNNING, [], "log")

        # This should not raise an exception, since attributes are processed
        job.to_json(dump=True)

        job_reloaded = Job.from_json(job.to_json())
        for attr in job.__dict__:
            if isinstance(job.__dict__[attr], timedelta):
                self.assertLess(abs(job.__dict__[attr].total_seconds() -
                                    job_reloaded.__dict__[attr].total_seconds()), 1)
            elif not callable(attr):
                self.assertEqual(job.__dict__[attr], job_reloaded.__dict__[attr])

                self.assertEqual(job.to_json(dump=True), job_reloaded.to_json(dump=True))

    def test_Arrayable(self):
        # This test is mostly here to make sure that attribute conversion works
        job = Job("job_id", "project_id", "job_name", "2000-01-01 00:00:00", "2020-01-01 00:00:00",
                  RunnableStatus.RUNNING, [], "log")

        # This should not raise an exception
        job.to_string_array(*[attr for attr in job.__dict__ if not callable(job.__dict__[attr])])


