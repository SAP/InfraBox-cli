import json
import os

import infraboxcli
from infraboxcli.log import logger
from v2infraboxapi import TokenKind, InfraBoxAPI


class LocalProjectConfig(object):
    """
    Class used to store a local project's config (InfraBox url, project id, ...).
    """

    def __init__(self, infrabox_url, project_id, infrabox_file):
        """
        :type infrabox_url: str
        :param infrabox_url: the InfraBox remote url
        :type project_id: str
        :param project_id: the project's id
        :param infrabox_file: the path to the InfraBox file or None
        """
        self.infrabox_url = infrabox_url
        self.project_id = project_id
        self._infrabox_file = None
        self.project_root = None
        self.project_name = None

        # Checks the presence of the file initializes the other attributes
        self.infrabox_file = infrabox_file

    @staticmethod
    def _get_local_config_file_path(project_root):
        """Returns the path to the local config file."""
        return os.path.join(project_root, ".local_config")

    def save(self):
        """Saves the local project's config in the project's root directory."""
        with open(self._get_local_config_file_path(self.project_root), "w") as f:
            json.dump(self.__dict__, f)

    @classmethod
    def from_json(cls, d):
        """Loads the config from a dict"""
        return cls(d["infrabox_url"],
                   d["project_id"],
                   d["_infrabox_file"])

    @classmethod
    def load(cls):
        """
        Tries to locate the project's root directory and to load the config file.
        If the root is found but the file is not, one will be created,
        but the project's id and the url will need to be set up.
        """
        p = os.getcwd()

        while p:
            tb = os.path.join(p, 'infrabox.json')
            if not os.path.exists(tb):
                tb = os.path.join(p, 'infrabox.yaml')
            if not os.path.exists(tb):
                p = p[0:p.rfind('/')]
            else:
                # Project root found!
                project_root = p
                infrabox_file = tb
                path = cls._get_local_config_file_path(project_root)

                # Is there a local config file?
                if os.path.isfile(path):
                    with open(path, "r") as f:
                        return cls.from_json(json.load(f))
                # Or else we need to create one
                logger.info("Local project config not found. Creating one.")
                logger.warn("Please specify the project's id using the config command.")
                ret = cls(infraboxcli.CLI_SETTINGS.infrabox_url,
                          "",
                          infrabox_file)
                ret.save()
                return ret

        logger.error("Local project root not found.")

    @property
    def infrabox_file(self):
        return self._infrabox_file

    @infrabox_file.setter
    def infrabox_file(self, infrabox_file):
        """
        Checks that the InfraBox file exists.
        :type infrabox_file: str
        :param infrabox_file: the path to an infrabox.json or infrabox.yaml file or None.
        """
        if infrabox_file:
            if not os.path.exists(infrabox_file):
                logger.error('%s does not exist' % infrabox_file)

            p = os.path.abspath(infrabox_file)

            self.project_root = p[0:p.rfind('/')]
            self._infrabox_file = p
            self.project_name = os.path.basename(p)

    def check_tokens(self):
        """Warns the user if no token has been found for this project's id."""
        if not self.project_id:
            logger.warn("Please specify the project's id using the config command.")
            return False

        manager = infraboxcli.CLI_TOKEN_MANAGER
        if manager.get_token(TokenKind.PULL, self.project_id) or manager.get_token(TokenKind.PUSH, self.project_id):
            return True

        logger.warn("No token has been found to pull/push on this project.")
        logger.warn("You might need to add one to the CLI by using the \"token save\" command.")
        return False

    def get_api(self):
        """
        Used to get an api instance with the right parameters for a local project.
        :rtype InfraBoxAPI
        :return: an api object to make REST calls
        """
        return InfraBoxAPI(self.infrabox_url,
                           infraboxcli.CLI_TOKEN_MANAGER,
                           ca_bundle=infraboxcli.CLI_SETTINGS.ca_bundle)
