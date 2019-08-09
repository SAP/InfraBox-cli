import unittest

from v2infraboxapi import Project, ProjectType


class TestProject(unittest.TestCase):
    def test_Arrayable(self):
        # Requries tests: test_User.test_Arrayable
        # This test is mostly here to make sure that attribute conversion works
        project = Project("project_id", "name", ProjectType.UPLOAD, True, "userrole")

        # This should not raise an exception
        project.to_string_array(*[attr for attr in project.__dict__ if not callable(project.__dict__[attr])])
