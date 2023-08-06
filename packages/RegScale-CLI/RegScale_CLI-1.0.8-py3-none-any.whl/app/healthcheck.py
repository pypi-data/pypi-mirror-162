#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

""" Healthcheck """
import sys

import requests
import yaml

from app.logz import create_logger

logger = create_logger()

#####################################################################################################
#
# REGSCALE HEALTHCHECK STATUS
#
#####################################################################################################
# check the status of RegScale instance


def status():
    """Get Status of Client Application"""
    config = {}
    try:
        # load the config from YAML
        with open("init.yaml", "r", encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
    except Exception:
        logger.error("ERROR: No init.yaml file or permission error when opening file.")

    # make sure config is set before processing
    if "domain" not in config:
        raise ValueError("ERROR: No domain set in the initilization file.")
    if config["domain"] == "":
        raise ValueError("ERROR: The domain is blank in the initialization file.")
    if (not "token" in config) or (config["token"] == ""):
        raise ValueError(
            "ERROR: The token has not been set in the initialization file."
        )
    # set health check URL
    url_login = config["domain"] + "/health"

    # get the health check data
    response = requests.request("GET", url_login)
    health_data = {}
    try:
        health_data = response.json()
    except Exception as ex:
        logger.error(
            "ERROR: Unable to retrieve health check data from RegScale: \n%s", ex
        )
        sys.exit()

    # output the result
    if "status" in health_data:
        if health_data["status"] == "Healthy":
            logger.info("System Status: Healthy")
        elif health_data["status"] == "Degraded":
            logger.warning("System Status: Degraded")
        elif health_data["status"] == "Unhealthy":
            logger.error("System Status: Unhealthy")
        else:
            logger.info("System Status: Unknown")
    else:
        raise ValueError("ERROR: No data returned from system health check.")

    # process checks
    if "entries" in health_data:
        checks = health_data["entries"]
        for chk in checks:
            logger.info("System: " + chk + ", Status: " + checks[chk]["status"])
    return health_data
