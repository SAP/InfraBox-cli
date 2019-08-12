import unittest

from v2infraboxapi import Build, Job, RunnableStatus


class TestBuild(unittest.TestCase):
    def test_Arrayable(self):
        # This test is mostly here to make sure that attribute conversion works

        # Not everything computed
        build = Build("project_id", "build_id", "build_number", "restart_coutner", False,
                      [Job("job_id", "project_id", "job_name", "2000-01-01 00:00:00", "2020-01-01 00:00:00",
                           RunnableStatus.RUNNING, [], "log")], dict())

        # This should not raise an exception
        build.to_string_array(*[attr for attr in build.__dict__ if not callable(build.__dict__[attr])])

        # Everything computed
        build = Build("project_id", "build_id", "build_number", "restart_coutner", False,
                      [Job("job_id", "project_id", "job_name", "2000-01-01 00:00:00", "2020-01-01 00:00:00",
                           RunnableStatus.RUNNING, [], "log")], dict())
        build.compute_jobs_related_information()
        self.assertIsNotNone(build.start_date)
        self.assertIsNotNone(build.duration)
        self.assertIsNotNone(build.status)

        # This should not raise an exception
        build.to_string_array(*[attr for attr in build.__dict__ if not callable(build.__dict__[attr])])
