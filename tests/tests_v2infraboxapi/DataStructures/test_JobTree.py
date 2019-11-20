import unittest

from v2infraboxapi import Job, JobTree, RunnableStatus


class TestJobTree(unittest.TestCase):
    def test_constructor_json(self):
        def job_factory(dependency):
            dependencies = [{"job-id": dependency}]
            job = Job("id" + str(job_factory.i), "", "", None, None, RunnableStatus.RUNNING, dependencies)
            job_factory.i += 1
            return job

        # This test is mostly here to test the tree building and json conversion

        # ======================================================================
        # Empty tree
        job_factory.i = 0

        # Building
        tree = JobTree([])
        self.assertEqual(len(list(iter(tree))), 0)

        # json
        tree2 = JobTree.from_json(tree.to_json())
        self.assertEqual(tree.root_nodes, tree2.root_nodes)

        # ======================================================================
        # Root node only (no dependencies)
        job_factory.i = 0

        # Building
        tree = JobTree([job_factory(None)])
        self.assertEqual(len(list(iter(tree))), 1)

        # json
        tree2 = JobTree.from_json(tree.to_json())
        for job, job2 in zip(tree, tree2):
            self.assertEqual(job.id, job2.id)

        # ======================================================================
        # One job but wrong dependency
        job_factory.i = 0

        # Building
        tree = JobTree([job_factory("id1")])
        self.assertEqual(len(list(iter(tree))), 0)

        # ======================================================================
        # Chained dependencies
        job_factory.i = 0

        # Building
        tree = JobTree([job_factory(None), job_factory("id0"), job_factory("id1")])
        self.assertEqual(len(list(iter(tree))), 3)

        # json
        tree2 = JobTree.from_json(tree.to_json())
        for job, job2 in zip(tree, tree2):
            self.assertEqual(job.id, job2.id)

        # ======================================================================
        # Multiple children
        job_factory.i = 0

        # Building
        tree = JobTree([job_factory(None), job_factory("id0"), job_factory("id0")])
        self.assertEqual(len(list(iter(tree))), 3)

        # json
        tree2 = JobTree.from_json(tree.to_json())
        for job, job2 in zip(tree, tree2):
            self.assertEqual(job.id, job2.id)
