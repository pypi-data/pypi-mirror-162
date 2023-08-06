#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

""" Application Configuration """
import os
import sys
from collections.abc import MutableMapping
from pathlib import Path

import yaml

from app.logz import create_logger


class Application(MutableMapping):
    """
    Regscale CLI configuration class
    """

    def __init__(self):
        """constructor"""

        """
        adAccessToken: Bearer <my token>
        adAuthUrl: https://login.microsoftonline.com/
        adClientId: <myclientidgoeshere>
        adGraphUrl: https://graph.microsoft.com/.default
        adSecret: <mysecretgoeshere>
        adTenantId: <mytenantidgoeshere>
        domain: https://dev.regscale.com/
        jiraApiToken: <jiraAPIToken>
        jiraUrl: <myJiraUrl>
        jiraUserName: <jiraUserName>
        snowPassword: <snowPassword>
        snowUrl: <mySnowUrl>
        snowUserName: <snowUserName>
        token: entertokenhere
        userId: <enter id here>
        wizAccessToken: <createdProgrammatically>
        wizAuthUrl: https://auth.wiz.io/oauth/token
        wizClientId: <myclientidgoeshere>
        wizClientSecret: <mysecretgoeshere>
        wizExcludes: My things to exclude here
        wizScope: <filled out programmatically after authenticating to Wiz>
        wizUrl: <my Wiz URL goes here>

        """

        template = {
            "domain": "https://mycompany.regscale.com/",
            "wizAccessToken": "<createdProgrammatically>",
            "wizClientId": "<myclientidgoeshere>",
            "wizClientSecret": "<mysecretgoeshere>",
            "wizScope": "<filled out programmatically after authenticating to Wiz>",
            "wizUrl": "<my Wiz URL goes here>",
            "wizAuthUrl": "https://auth.wiz.io/oauth/token",
            "wizExcludes": "My things to exclude here",
            "adAuthUrl": "https://login.microsoftonline.com/",
            "adGraphUrl": "https://graph.microsoft.com/.default",
            "adAccessToken": "Bearer <my token>",
            "adClientId": "<myclientidgoeshere>",
            "adSecret": "<mysecretgoeshere>",
            "adTenantId": "<mytenantidgoeshere>",
            "jiraUrl": "<myJiraUrl>",
            "jiraUserName": "<jiraUserName>",
            "jiraApiToken": "<jiraAPIToken>",
            "snowUrl": "<mySnowUrl>",
            "snowUserName": "<snowUserName>",
            "snowPassword": "<snowPassword>",
            "userId": "enter user id here",
            "oscal_location": "/opt/OSCAL",
            "saxon_path": "/opt/saxon-he-11.4.jar",
        }
        logger = create_logger()
        self.template = template
        self.templated = False
        self.logger = logger
        env = self._get_env()
        yaml_env = self._get_conf()
        config = self._gen_config()
        self.config = config
        if not Path(self.config["oscal_location"]).exists():
            logger.warning("OSCAL folder path does not exist, please check init.yaml")

    def __getitem__(self, key):
        """Get an item."""
        return self.config.__getitem__(self, key)

    def __setitem__(self, key, value):
        """Set an item."""

        value = int(value)
        if not 1 <= value <= 10:
            raise ValueError(f"{value} not in range [1,10]")
        self.config.__setitem__(self, key, value)

    def __delitem__(self, key):
        """Delete an item."""

        self.config.__delitem__(self, key)

    def __iter__(self):
        """return iterator"""
        return self.config.__iter__(self)

    def __len__(self):
        """get the length of the config."""

        return self.config.__len__(self)

    def __contains__(self, x: str):
        """Check config if it contains string."""

        return self.config.__contains__(self, x)

    def _gen_config(self) -> dict:
        config = None
        try:
            env = self._get_env()
            file_config = self._get_conf()
            self.logger.debug("file_config: %s", file_config)
            # Merge
            if self.templated is False:
                config = {**file_config, **env}
            else:
                config = {**env, **file_config}
            self.logger.debug("merged begin: %s", config)

        except Exception as e:
            self.logger.error("No configuration loaded!!! Exiting.. %s", e)
            sys.exit()
        if config is not None:
            try:
                with open(r"init.yaml", "w", encoding="utf-8") as file:
                    yaml.dump(config, file)
            except OSError:
                self.logger.error("Could not dump config to init.yaml")
        # Return config
        self.logger.debug("merged end: %s", config)
        return config

    def _get_env(self) -> dict:
        """return dict of regscale keys from system"""
        all_keys = self.template.keys()
        sys_keys = [key for key in os.environ if key in all_keys]
        #  Update Template
        dat = None
        try:
            dat = self.template.copy()
            for k in sys_keys:
                dat[k] = os.environ[k]
        except Exception as ex:
            self.logger.error("Key Error!!: %s", ex)
        self.logger.debug("dat: %s", dat)
        if dat == self.template:
            # Is the generated data the same as the template?
            self.templated = True
        return dat

    def _get_conf(self) -> dict:
        """Get configuration from init.yaml if exists"""
        config = None
        fname = "init.yaml"
        # load the config from YAML
        try:
            with open(fname, encoding="utf-8") as stream:
                config = yaml.safe_load(stream)

        except Exception as e:
            self.logger.error(e)
        self.logger.debug("_get_conf: %s, %s", config, type(config))
        return config
