#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

import json

import click
import msal
import requests
import yaml

from app.application import Application
from app.logz import create_logger

logger = create_logger()


# Create group to handle Active Directory processing
@click.group()
def ad():
    """Performs directory and user synchronization functions with Azure Active Directory"""
    pass


#####################################################################################################
#
# AUTHENTICATE TO ACTIVE DIRECTORY
#
#####################################################################################################
@ad.command()
def authenticate():
    """Obtains an access token using the credentials provided"""
    getAccessToken()


#####################################################################################################
#
# GET ACTIVE DIRECTORY GROUPS
#
#####################################################################################################
@ad.command()
def listGroups():
    """Prints the lists of available RegScale groups the CLI can read"""
    # authenticate the user
    getAccessToken()

    # list all of the groups
    listADGroups()


#####################################################################################################
#
# SYNC REGSCALE ADMINS FROM ACTIVE DIRECTORY
#
#####################################################################################################
@ad.command()
def syncAdmins():
    """Syncs members of the regscale-admins group and assigns roles"""
    # authenticate the user
    getAccessToken()

    # set the Microsoft Graph Endpoint
    getGroup("regscale-admin")


#####################################################################################################
#
# SYNC REGSCALE GENERAL USERS FROM ACTIVE DIRECTORY
#
#####################################################################################################
@ad.command()
def syncGeneral():
    """Syncs members of the regscale-general group and assigns roles"""
    # authenticate the user
    getAccessToken()

    # set the Microsoft Graph Endpoint
    getGroup("regscale-general")


#####################################################################################################
#
# SYNC REGSCALE READ ONLY FROM ACTIVE DIRECTORY
#
#####################################################################################################
@ad.command()
def syncReadonly():
    """Syncs members of the regscale-readonly group and assigns roles"""
    # authenticate the user
    getAccessToken()

    # set the Microsoft Graph Endpoint
    getGroup("regscale-readonly")


#############################################################################
#
#   Supporting Functions
#
#############################################################################


def CheckConfig(strKey, strTitle, config):
    def error(str):
        logger.error(f"ERROR: No Azure AD {strTitle} set in the init.yaml file.")

    if strKey not in config:
        error(strTitle)
        quit()
    elif config[strKey] == None:
        error(strTitle)
        quit()
    elif config[strKey] == "":
        error(strTitle)
        quit()


def getAccessToken():
    appl = Application()

    config = appl.config
    # load the config from YAML
    # with open("init.yaml", "r") as stream:
    #     config = yaml.safe_load(stream)

    # validation for each field
    CheckConfig("adClientId", "Client ID", config)
    CheckConfig("adTenantId", "Tenant ID", config)
    CheckConfig("adSecret", "Secret", config)
    CheckConfig("adGraphUrl", "Graph URL", config)
    CheckConfig("adAuthUrl", "Authentication URL", config)

    # generate the endpoint
    authURL = config["adAuthUrl"] + str(config["adTenantId"])
    graphURL = config["adGraphUrl"]

    # configure the Microsoft MSAL library to authenticate and gain an access token
    app = msal.ConfidentialClientApplication(
        config["adClientId"],
        authority=authURL,
        client_credential=config["adSecret"],
    )

    # use MSAL to get the token (no caching for security)
    try:
        token = app.acquire_token_for_client(scopes=graphURL)
        config["adAccessToken"] = "Bearer " + token["access_token"]

        # write the changes back to file
        with open(r"init.yaml", "w") as file:
            documents = yaml.dump(config, file)
            logger.info("Azure AD Login Successful!")
            logger.info("Init.yaml file updated successfully with the access token.")
    except:
        logger.error("ERROR: Unable to authenticate to Azure AD")
        quit()

    # return the result
    return token


# lists all RegScale groups in AD
def listADGroups():
    # load the config from YAML
    with open("init.yaml", "r") as stream:
        config = yaml.safe_load(stream)

    # validate
    CheckConfig("adAccessToken", "Access Token", config)
    CheckConfig("adGraphUrl", "Graph URL", config)

    # trim the URL
    strGraphUrl = config["adGraphUrl"].replace(".default", "")

    # set the endpoint
    groupsURL = strGraphUrl + "v1.0/groups?$filter=startswith(displayName,'regscale')"

    # setup the header
    headers = {"Authorization": config["adAccessToken"]}

    # get the AD group info
    logger.info("Fetching relevant AD Groups from Azure for RegScale")
    try:
        groupsResponse = requests.request("GET", groupsURL, headers=headers)
        groupsData = groupsResponse.json()
    except:
        logger.error(
            "ERROR: Unable to retrieve group information from Azure Active Directory."
        )
        quit()

    # loop through the groups and log the results
    if "value" in groupsData:
        for g in groupsData["value"]:
            logger.info("GROUP: " + g["displayName"])
        logger.info(str(len(groupsData["value"])) + " total groups retrieved.")
    else:
        # error handling (log error)
        if "error" in groupsData:
            try:
                logger.error()
                print(
                    groupsData["error"]["code"] + ": " + groupsData["error"]["message"]
                )
            except:
                logger.error()
                logger.error("Unknown Error!")
                logger.error(groupsData)

    # write out group data to file
    with open("artifacts/regscale-AD-groups.json", "w") as outfile:
        outfile.write(json.dumps(groupsData, indent=4))


# retrieves the RegScale groups from Azure AD
def getGroup(strGroup):
    """Syncs members of the regscale-admins group and assigns roles"""
    # variables
    newUsers = []
    removeUsers = []

    # see if readonly
    bReadOnly = False
    if strGroup == "regscale-readonly":
        bReadOnly = True

    # load the config from YAML
    with open("init.yaml", "r") as stream:
        config = yaml.safe_load(stream)

    # validate and trim the Graph URL
    CheckConfig("adAccessToken", "Access Token", config)
    CheckConfig("adGraphUrl", "Graph URL", config)
    strGraphUrl = config["adGraphUrl"].replace(".default", "")

    # set the Microsoft Graph Endpoint
    if strGroup == "regscale-admin":
        groupsURL = (
            strGraphUrl + "v1.0/groups?$filter=startswith(displayName,'regscale-admin')"
        )
    elif strGroup == "regscale-general":
        groupsURL = (
            strGraphUrl
            + "v1.0/groups?$filter=startswith(displayName,'regscale-general')"
        )
    elif strGroup == "regscale-readonly":
        groupsURL = (
            strGraphUrl
            + "v1.0/groups?$filter=startswith(displayName,'regscale-readonly')"
        )
    else:
        logger.error(
            "ERROR: Unknown RegScale group (" + strGroup + ") requested for sync"
        )

    # setup the header
    headers = {"Authorization": config["adAccessToken"]}

    # get the AD group info
    logger.info("Fetching relevant AD Groups from Azure for RegScale")
    try:
        groupsResponse = requests.request("GET", groupsURL, headers=headers)
        groupsData = groupsResponse.json()
    except:
        logger.error(
            "ERROR: Unable to retrieve group information from Azure Active Directory."
        )
        quit()

    # write out group data to file
    with open("artifacts/adGroupList-" + strGroup + ".json", "w") as outfile:
        outfile.write(json.dumps(groupsData, indent=4))

    # loop through each group to find admins
    if len(groupsData) == 0:
        logger.error(
            "ERROR: " + strGroup + " group has not been setup yet in Azure AD."
        )
        quit()
    else:
        # get group info
        if "value" in groupsData:
            foundGroup = groupsData["value"][0]
            groupId = foundGroup["id"]
        else:
            # error handling (log error)
            if "error" in groupsData:
                try:
                    logger.error(
                        groupsData["error"]["code"]
                        + ": "
                        + groupsData["error"]["message"]
                    )
                    quit()
                except:
                    logger.error("Unknown Error!")
                    logger.error(groupsData)
                    quit()

        # get AD group members
        membersURL = strGraphUrl + "v1.0/groups/" + str(groupId) + "/members"

        # get the member list for the AD group
        print("Fetching the list of members for this AD group - " + str(groupId))
        try:
            memberResponse = requests.request("GET", membersURL, headers=headers)
            memberData = memberResponse.json()
        except:
            logger.error(
                "ERROR: Unable to retrieve member list for Azure Active Directory group - "
                + str(groupId)
            )
            quit()

        # write out member data to file
        with open("artifacts/adMemberList-" + str(groupId) + ".json", "w") as outfile:
            outfile.write(json.dumps(memberData, indent=4))
        print(memberData)
        # retrieve the list of RegScale users
        urlUsers = config["domain"] + "/api/accounts/getList"
        regScaleHeaders = {"Authorization": config["token"]}
        try:
            userResponse = requests.request("GET", urlUsers, headers=regScaleHeaders)
            userData = userResponse.json()
        except:
            logger.error("ERROR: Unable to retrieve user list from RegScale")
            quit()

        # retrieve the list of RegScale roles
        urlRoles = config["domain"] + "/api/accounts/getRoles"
        try:
            roleResponse = requests.request("GET", urlRoles, headers=regScaleHeaders)
            roleData = roleResponse.json()
        except:
            logger.error("ERROR: Unable to retrieve roles from RegScale")
            quit()

        # loop through the members of the AD group (create new if not in RegScale)
        for m in memberData["value"]:
            # see if it exists
            bMemberFound = False
            for u in userData:
                if "externalId" in u:
                    if m["id"] == u["externalId"]:
                        bMemberFound = True

            # handle new user flow
            if bMemberFound == False:
                # create a new user
                newUser = {
                    "id": "",
                    "userName": m["userPrincipalName"],
                    "email": m["mail"],
                    "password": "",
                    "firstName": m["givenName"],
                    "lastName": m["surname"],
                    "workPhone": m["mobilePhone"],
                    "pictureURL": "",
                    "activated": True,
                    "jobTitle": m["jobTitle"],
                    "orgId": None,
                    "emailNotifications": True,
                    "tenantId": 1,
                    "ldapUser": True,
                    "externalId": m["id"],
                    "dateCreated": None,
                    "lastLogin": None,
                    "readOnly": bReadOnly,
                }
                newUsers.append(newUser)

        # loop through the users (disable if not in AD group)
        for u in userData:
            if "externalId" in u:
                bDisable = True
                for m in memberData["value"]:
                    if m["id"] == u["externalId"]:
                        bDisable = False
                if bDisable == True:
                    removeUsers.append(u)

        # write out new user list to file
        with open("artifacts/newUsers.json", "w") as outfile:
            outfile.write(json.dumps(newUsers, indent=4))

        # write out disabled user list to file
        with open("artifacts/removeUsers.json", "w") as outfile:
            outfile.write(json.dumps(removeUsers, indent=4))

        # Logging
        logger.info(str(len(newUsers)) + " new users to process.")

        # loop through each user
        regscaleNew = []
        for us in newUsers:
            # add new users in bulk
            urlNewUsers = config["domain"] + "/api/accounts/azureAD"
            regScaleHeaders = {"Authorization": config["token"]}
            try:
                strUser = requests.request(
                    "POST", urlNewUsers, headers=regScaleHeaders, json=us
                )
                userNew = {"id": strUser.text}
                regscaleNew.append(userNew)
                logger.info("User created or updated: " + us["userName"])
            except Exception as e:
                logger.error("ERROR: Unable to create new user" + us["userName"])
                print(e)
                quit()

        # write out new user list to file
        with open("artifacts/newRegscaleUsers.json", "w") as outfile:
            outfile.write(json.dumps(regscaleNew, indent=4))

        # set the role
        strRole = ""
        if strGroup == "regscale-admin":
            strRole = "Administrator"
        elif strGroup == "regscale-general":
            strRole = "GeneralUser"
        elif strGroup == "regscale-readonly":
            strRole = "ReadOnly"

        # set the RegScale role based on the AD group
        regScaleRole = None
        for r in roleData:
            if r["name"] == strRole:
                regScaleRole = r
        if r == None:
            logger.error("Error: Unable to locate RegScale role for group: " + strGroup)
            quit()

        # loop through the users and assign roles
        intRoles = 0
        for us in regscaleNew:
            # check the role
            urlCheckRole = (
                config["domain"]
                + "/api/accounts/checkRole/"
                + us["id"]
                + "/"
                + regScaleRole["id"]
            )
            try:
                roleCheck = requests.request(
                    "GET", urlCheckRole, headers=regScaleHeaders
                )
                strCheck = roleCheck.text
            except Exception as e:
                logger.error(
                    "ERROR: Unable to check role: "
                    + us["id"]
                    + "/"
                    + regScaleRole["id"]
                )
                quit()

            # add the role
            if strCheck == "false":
                # add the role
                urlAssignRole = config["domain"] + "/api/accounts/assignRole/"
                # role assignment object
                assign = {"roleId": regScaleRole["id"], "userId": us["id"]}
                try:
                    roleAssign = requests.request(
                        "POST", urlAssignRole, headers=regScaleHeaders, json=assign
                    )
                    intRoles += 1
                except Exception as e:
                    logger.error(
                        "ERROR: Unable to assign role: "
                        + us["id"]
                        + "/"
                        + regScaleRole["id"]
                    )
                    quit()

        # output results
        if intRoles > 0:
            print("Total Roles Assigned: " + str(intRoles))

        # loop through and remove users
        intRemovals = 0
        for us in removeUsers:
            # check the role
            urlCheckRole = (
                config["domain"]
                + "/api/accounts/checkRole/"
                + us["id"]
                + "/"
                + regScaleRole["id"]
            )
            try:
                roleCheck = requests.request(
                    "GET", urlCheckRole, headers=regScaleHeaders
                )
                strCheck = roleCheck.text
            except Exception as e:
                logger.error(
                    "ERROR: Unable to check role: "
                    + us["id"]
                    + "/"
                    + regScaleRole["id"]
                )
                quit()

            # add the role
            if strCheck == "true":
                # remove the role
                urlRemoveRole = (
                    config["domain"]
                    + "/api/accounts/deleteRole/"
                    + us["id"]
                    + "/"
                    + regScaleRole["id"]
                )
                try:
                    roleRemove = requests.request(
                        "DELETE", urlRemoveRole, headers=regScaleHeaders
                    )
                    intRemovals += 1
                except Exception as e:
                    logger.error(
                        "ERROR: Unable to remove role: "
                        + us["id"]
                        + "/"
                        + regScaleRole["id"]
                    )
                    quit()

                # deactive the user if they were in this role
                urlDeactivate = (
                    config["domain"]
                    + "/api/accounts/changeUserStatus/"
                    + us["id"]
                    + "/false"
                )
                try:
                    activation = requests.request(
                        "GET", urlDeactivate, headers=regScaleHeaders
                    )
                    logger.warning(us["userName"] + " account deactivated.")
                except Exception:
                    logger.error(
                        "ERROR: Unable to check role: "
                        + us["id"]
                        + "/"
                        + regScaleRole["id"]
                    )
                    quit()

        # output results
        logger.info(
            str(intRemovals) + " users had roles removed and accounts disabled."
        )
