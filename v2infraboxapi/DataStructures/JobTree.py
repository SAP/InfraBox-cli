# -*- coding: utf-8 -*-
import json

from v2infraboxapi.Utils import DefaultDict
from .Job import Job
from .RunnableStatus import RunnableStatus


class JobTree(object):
    """
    Class used to store jobs and display their dependencies. Only the first dependency is stored.
    """

    def __init__(self, jobs):
        """
        :param jobs: an iterable containing jobs, but above all every job mentioned in the dependencies
        """
        dependencies_dict = DefaultDict(list)  # {dependency: [jobs depending on it]}

        # Temporarily storing the dependencies as a dict for tree building
        for job in jobs:  # type: Job
            dependencies_dict[job.dependencies[0]["job-id"] if job.dependencies else None].append(job)

        # Building the tree
        self.root_nodes = TreeNode.build_trees_from_dependencies_dict(dependencies_dict)

    def __str__(self):
        return "\n".join([str(node) for node in self.root_nodes])

    def __iter__(self):
        for root_node in self.root_nodes:
            for content in root_node:
                yield content

    def to_json(self, dump=False):
        ret = {"root_nodes": [node.to_json() for node in self.root_nodes]}
        return json.dumps(ret) if dump else ret

    @classmethod
    def from_json(cls, json_dict):
        ret = cls([])
        ret.root_nodes = [TreeNode.from_json(node) for node in json_dict["root_nodes"]]
        return ret


class TreeNode(object):
    """
    Internal class used to store a tree node
    """

    def __init__(self, children, job):
        """
        :type children: list
        :param children: a list of tree nodes representing the node's children
        :type job: Job
        :param job: the job stored in this node
        """
        self.children = sorted(children, key=lambda node: node.job.name)
        self.job = job

    def __iter__(self):
        yield self.job
        for child in self.children:
            for content in child:
                yield content

    def __str__(self):
        ret = self.__unicode__()
        if not isinstance(ret, str):
            # Then this is Python 2 as Python 3 recognizes unicode as string
            ret = ret.encode("UTF-8")
        return ret

    def __unicode__(self):
        def node_to_string(node, indent):
            # Erasing unnecessary indenting
            indent = indent[:-4].replace(u'─', u' ').replace(u'└', u' ').replace(u'├', u'│') + indent[-4:]

            ret = u""
            # Adding the current node
            status = RunnableStatus.to_short_string(node.job.status) if node.job.status else ""

            ret += indent + node.job.name + u" " + status + u"\n"
            # Displaying the job's id in the next line -> need to update the indent
            ret += indent.replace(u'─', u' ').replace(u'├', u'│').replace(u'└', u' ') + node.job.id + u"\n"

            if node.children:
                # Handles every child except the last one
                for child in node.children[:-1]:
                    ret += node_to_string(child, indent + u"├───")

                # The last child gets some special treatment
                last_child = node.children[-1]
                ret += node_to_string(last_child, indent + u"└───")

            return ret

        return node_to_string(self, u"")

    @staticmethod
    def build_trees_from_dependencies_dict(dep_dict, no_dep_key=None):
        """
        :type dep_dict: dict
        :param dep_dict: a dictionary {dependency: [jobs depending on it]}
        :type no_dep_key: str
        :param no_dep_key: key used to refer to jobs without a dependency (used to recursively build the tree)
        :rtype list
        :return: a list of trees representing the dependencies
        (there will be as many trees as there are jobs without any dependency)
        """
        root_nodes = []
        # For each root job
        for job in dep_dict[no_dep_key]:
            # We first get the list of children's nodes
            children = TreeNode.build_trees_from_dependencies_dict(dep_dict, job.id)
            # We can then create the node for this job
            root_nodes.append(TreeNode(children, job))
        return root_nodes

    def to_json(self, dump=False):
        ret = dict()
        ret["children"] = [child.to_json() for child in self.children]
        ret["job"] = self.job.to_json()
        return json.dumps(ret) if dump else ret

    @classmethod
    def from_json(cls, json_dict):
        return cls(children=[TreeNode.from_json(node) for node in json_dict["children"]],
                   job=Job.from_json(json_dict["job"]))
