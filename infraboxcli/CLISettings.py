import json
import os
from datetime import datetime

import infraboxcli
from v2infraboxapi import InfraBoxAPI, Build
from .Utils import CLI_DATA_DIR, locked
from .log import logger


class CLISettings(object):
    """
    Class used to save recently listed objects like Build or Job.
    Keys: builds: {build_id: Build()}
          jobs: {job_id: Job()}
          cache_timestamp: datetime()
          id_env: {"project_id" : project_id, "build_id": build_id, "job_id": job_id}, id_env where we store last used ids
    """
    _SAVE_PATH = os.path.join(CLI_DATA_DIR, "cli_settings")
    _LOCKFILE_PATH = os.path.join(CLI_DATA_DIR, "settings_lockfile.pid")

    def __init__(self):
        super(CLISettings, self).__init__()

        # Stored information
        # Build cache
        self.cached_builds = dict()
        self.cache_timestamp = datetime.now()
        # Id env
        self.id_env = {"project_id": None, "build_id": None, "job_id": None}
        # Id history
        self.id_history = {"project_id": set(), "build_id": set(), "job_id": set()}
        # Project name to id
        self.known_project_names = dict()

        # API settings
        # Default settings for SAP users
        self._ca_bundle = False
        self.infrabox_url = ""
        # Grid style
        self.grid_style = "simple"

    def add_build_to_cache(self, build):
        """
        Adds a build to the cached builds. Clears the cache if needed.
        :type build: Build
        """
        self.clear_cache()
        self.cached_builds[build.id] = build
        self.cache_timestamp = datetime.now()

    def get_build_from_cache(self, build_id, default=None):
        """
        Returns a build from the cached builds. Clears the cache if needed.
        :param build_id: the build's id
        :param default: a default value to return if the build is not found in the cache
        :return: the cached build if possible or else the default value
        """
        self.clear_cache()
        return self.cached_builds.get(build_id, default)

    @locked(_LOCKFILE_PATH)
    def save(self, save_env_settings=False):
        """
        Saves the settings to the hard drive by converting everything stored to json.
        Uses a lockfile to avoid save conflicts.
        :type save_env_settings: bool
        :param save_env_settings: whether we should save settings regarding the env
        """

        data_keys = ["cached_builds", "cache_timestamp", "id_history", "known_project_names", "id_env"]
        api_keys = ["_ca_bundle", "infrabox_url", "grid_style"]

        old_settings = self._load().to_json()
        cur_settings = self.to_json()

        # Updating old settings
        old_settings.update({key: cur_settings[key] for key in data_keys + (api_keys if save_env_settings else [])})

        with open(CLISettings._SAVE_PATH, "w") as f:
            json.dump(old_settings, f)

    def to_json(self):
        """
        Converts a CLISettings to a dict.
        :rtype dict
        """
        ret = self.__dict__.copy()
        ret["cache_timestamp"] = self.cache_timestamp.strftime("%d/%m/%Y %H:%M:%S")
        ret["cached_builds"] = {key: self.cached_builds[key].to_json() for key in self.cached_builds}
        ret["id_history"] = {key: list(self.id_history[key]) for key in self.id_history}
        return ret

    @classmethod
    @locked(_LOCKFILE_PATH)
    def load(cls):
        """Loads the settings from the hard drive if found. (Uses a lockfile)"""
        return cls._load()

    @classmethod
    def _load(cls):
        """Raw code to load the settings. (Not thread safe)"""
        if not os.path.isfile(cls._SAVE_PATH):
            return cls()

        with open(cls._SAVE_PATH, "r") as f:
            try:
                settings = cls.from_json(json.load(f))

                # Deleting the cache if it's too old
                settings.clear_cache()
                return settings

            except:
                logger.exception()
                logger.warn("An error occurred while loading the cache. It has been cleared.")
                os.remove(cls._SAVE_PATH)
                return cls()

    @classmethod
    def from_json(cls, json_dict):
        """
        Converts a dict to a CLISettings object.
        :type json_dict: dict
        """
        settings = cls()

        settings.cached_builds = {key: Build.from_json(json_dict["cached_builds"][key])
                                  for key in json_dict["cached_builds"]}
        settings.cache_timestamp = datetime.strptime(json_dict["cache_timestamp"], "%d/%m/%Y %H:%M:%S")
        settings.id_env = json_dict["id_env"]
        settings.id_history = {key: set(json_dict["id_history"][key]) for key in json_dict["id_history"]}
        settings.ca_bundle = json_dict["_ca_bundle"]
        settings.infrabox_url = json_dict["infrabox_url"]
        settings.grid_style = json_dict["grid_style"]
        settings.known_project_names = json_dict["known_project_names"]

        return settings

    def clear_cache(self, force=False):
        """Clears the cache if it's too old."""
        if (datetime.now() - self.cache_timestamp).total_seconds() > 300 or force:
            self.cached_builds = dict()

    def clear_history(self, keys):
        """Clears the history for the specified kinds of ids (project_id, build_id, job_id)"""
        for kind in keys:
            if kind not in self.id_history:
                raise KeyError(kind)
            self.id_history[kind] = set()

    def clear_known_project_names(self):
        """Clears the known project names."""
        self.known_project_names = dict()

    def get_from_env(self, id_value, key, raise_exception=True):
        """
        If value is None, gets the right value from the id_env.
        If value is not None, sets it in the id_env.
        Also updates the id history.
        :param id_value: an id
        :type key: str
        :param key: "project_id" or "build_id" or "job_id"
        :type raise_exception: bool
        :param: whether we should raise an exception if the value stored is None
        """
        if key not in self.id_env:
            return id_value

        if id_value is not None:
            self.id_env[key] = id_value
            self.id_history[key].add(id_value)
            return id_value
        else:
            if self.id_env[key] is None and raise_exception:
                logger.error("Id " + str(key.upper()) + " missing from env / command arguments.")
            return self.id_env[key]

    def completion_from_history(self, incomplete, key):
        """
        Tries to complete the incomplete id and returns a list of possibilities
        :type incomplete: str
        :param incomplete: beginning of an id
        :type key: str
        :param key: "project_id" or "build_id" or "job_id"
        :rtype list
        :return a list of possible ids
        """
        return list(filter(lambda string: string.startswith(incomplete) if string else False,
                           self.id_history.get(key, [])))

    def get_api(self):
        """
        Used to get an api instance with the right parameters across the CLI
        :rtype InfraBoxAPI
        :return: an api object to make REST calls
        """
        return InfraBoxAPI(self.infrabox_url, infraboxcli.CLI_TOKEN_MANAGER, ca_bundle=self.ca_bundle)

    # Settings properties
    @property
    def ca_bundle(self):
        return self._ca_bundle

    @ca_bundle.setter
    def ca_bundle(self, ca_bundle):
        """
        :type ca_bundle: str
        :param ca_bundle: the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
        """
        if ca_bundle:
            if not os.path.exists(ca_bundle):
                logger.error("INFRABOX_CA_BUNDLE: %s not found" % ca_bundle)
            self._ca_bundle = ca_bundle

    @classmethod
    def delete(cls):
        """Deletes the settings from the hard drive."""
        if os.path.isfile(cls._SAVE_PATH):
            os.remove(cls._SAVE_PATH)


CLI_SETTINGS = CLISettings.load()
