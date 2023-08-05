#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from json import JSONDecodeError
import logging
import requests
import sys
import yaml
import app.healthcheck as hc
from app.application import Application
from app.logz import create_logger

logger = create_logger()
appl = Application()
config = appl.config
#####################################################################################################
#
# LOGIN TO REGSCALE
#
#####################################################################################################
# logs in the user
def login(strUser, strPassword):
    jwt = None
    # load the config from YAML
    # with open("init.yaml", "r") as stream:
    #     config = yaml.safe_load(stream)
    if config["domain"] is None:
        raise ValueError("ERROR: No domain set in the initilization file.")
    elif config["domain"] == "":
        raise ValueError("ERROR: The domain is blank in the initialization file.")
    else:
        # set the catalog URL for your Atlasity instance
        url_login = config["domain"] + "/api/authentication/login"
        logger.info("Logging into: " + url_login)

        # create object to authenticate
        auth = {"userName": strUser, "password": strPassword, "oldPassword": ""}
        logging.debug(auth)
        if is_valid() is False and auth["password"]:
            try:
                userId, jwt = regscale_login(url_login, auth)

                # update init file from login
                config["token"] = jwt
                config["userId"] = userId

                # write the changes back to file
                with open(r"init.yaml", "w") as file:
                    logger.debug(f"Dumping config {config}")
                    yaml.dump(config, file)
                    logger.info("Login Successful!")
                    logger.info("Init.yaml file updated successfully.")

                # set variables
                logger.info("User ID: " + userId)
                logger.info("RegScale Token: " + jwt)
            except TypeError as e:
                pass
                # logger.error("TypeError: %s", e)
        jwt = config["token"]

    return jwt


def regscale_login(url_login, auth):
    try:
        # login and get token
        response = requests.request("POST", url_login, json=auth)
        authResponse = response.json()
        userId = authResponse["id"]
        jwt = "Bearer " + authResponse["auth_token"]
        logging.debug(jwt)

    except ConnectionError as e:
        logger.error(
            "ConnectionError: Unable to login user to RegScale, check the server domain"
        )
        quit()
    except JSONDecodeError as d:
        logger.error("Login Error: Unable to login user to RegScale")
        quit()
    return userId, jwt


def is_valid():
    """Quick endpoint to check login status"""
    login_status = False
    try:
        # Make sure url isn't default
        # login with token
        token = config["token"]
        headers = {f"Authorization": token}
        url_login = config["domain"] + f"/api/logging/filterLogs/1/1"
        logger.debug("is_valid url: %s", url_login)
        logger.debug("is_valid headers: %s", headers)
        response = requests.request("GET", url_login, headers=headers)
        if response:
            if response.status_code == 200:
                login_status = True
    except Exception as e:
        logger.error(e)
    except TypeError(e):
        pass
    except ConnectionError as e:
        logger.error(
            "ConnectionError: Unable to login user to RegScale, check the server domain"
        )
    except JSONDecodeError as d:
        logger.error("Login Error: Unable to login user to RegScale")
        logger.error(d)
    finally:
        logger.debug("login status: %s", login_status)
        return login_status
