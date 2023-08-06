import json
import os.path

import click
import requests
import yaml
from jira import JIRA

from app.logz import create_logger


# Create group to handle Jira integration
@click.group()
def jira():
    """Auto-assigns tickets to JIRA for remediation"""
    pass


#####################################################################################################
#
# PROCESS ISSUES TO JIRA
# JIRA CLI Python Docs: https://jira.readthedocs.io/examples.html#issues
# JIRA API Docs: https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
#
#####################################################################################################
@jira.command()
@click.option(
    "--issue_level",
    prompt="Enter the Level of Issues to Process",
    help="RegScale will process all issues this level or higher.  Options include: LOW, MEDIUM, HIGH, CRITICAL.",
)
@click.option(
    "--regscale_id",
    prompt="Enter the RegScale Record ID",
    help="RegScale will create and update issues as children of this record.",
)
@click.option(
    "--regscale_module",
    prompt="Enter the RegScale Module name",
    help="Enter the RegScale module.  Options include: projects, policies, supplychain, securityplans, components.",
)
@click.option(
    "--jira_project",
    prompt="Enter the name of the project in Jira",
    help="RegScale will sync the issues for the record to the Jira project.",
)
@click.option(
    "--jira_issue_type",
    prompt="Enter the Jira issue type",
    help="Enter the Jira issue type to use when creating new issues from RegScale",
)
def issues(issue_level, regscale_id, regscale_module, jira_project, jira_issue_type):
    """Process issues to Jira"""
    logger = create_logger()
    # check issue level parameter
    if (
        str(issue_level).upper() != "LOW"
        and str(issue_level).upper() != "MEDIUM"
        and str(issue_level).upper() != "HIGH"
        and str(issue_level).upper() != "CRITICAL"
    ):
        logger.error(
            "You must select one of the following issue levels: LOW, MEDIUM, HIGH, CRITICAL"
        )
        quit()

    # load the config from YAML
    with open("init.yaml", "r") as stream:
        config = yaml.safe_load(stream)

    # get secrets
    url = config["jiraUrl"]
    domain = config["domain"]
    token = config["jiraApiToken"]
    strUser = config["userId"]
    jiraUser = config["jiraUserName"]

    # set headers
    url_issues = (
        config["domain"]
        + "/api/issues/getAllByParent/"
        + str(regscale_id)
        + "/"
        + str(regscale_module).lower()
    )
    regScaleHeaders = {"Accept": "application/json", "Authorization": config["token"]}
    updateHeaders = {"Authorization": config["token"]}

    # get the existing issues for the parent record that are already in RegScale
    logger.info("Fetching full issue list from RegScale")
    issueResponse = requests.request("GET", url_issues, headers=regScaleHeaders)
    # check for null/not found response
    if issueResponse.status_code == 204:
        logger.warning("No existing issues for this RegScale record.")
        issuesData = []
    else:
        try:
            issuesData = issueResponse.json()
        except:
            logger.error("Unable to fetch issues from RegScale")
            quit()

    # make directory if it doesn't exist
    if os.path.exists("./artifacts") == False:
        os.mkdir("./artifacts")
        logger.warning(
            "Artifacts directory does not exist.  Creating new directory for artifact processing."
        )
    else:
        logger.info(
            "Artifacts directory exists.  This directly will store output files from all processing."
        )

    # write out issues data to file
    if len(issuesData) > 0:
        with open("artifacts/existingRecordIssues.json", "w") as outfile:
            outfile.write(json.dumps(issuesData, indent=4))
        logger.info(
            "Writing out RegScale issue list for Record #"
            + str(regscale_id)
            + " to the artifacts folder (see existingRecordIssues.json)"
        )
    logger.info(
        str(len(issuesData))
        + " existing issues retrieved for processing from RegScale."
    )

    # set the JIRA Url
    jiraClient = JIRA(basic_auth=(jiraUser, token), options={"server": url})
    startPointer = 0
    pageSize = 100
    jiraIssues = []

    # get all issues for the Jira project
    while True:
        start = startPointer * pageSize
        fetchIssues = jiraClient.search_issues(
            "project=" + jira_project,
            fields="key,summary,description,status",
            startAt=start,
            maxResults=pageSize,
        )
        logger.info(str(len(fetchIssues)) + " issues retrieved.")
        if len(fetchIssues) == 0:
            logger.info("All done here")
            break
        else:
            logger.info("Going to the next step")
            startPointer += 1
            for iss in fetchIssues:
                jiraIssues.append(iss)

    # loop through each RegScale issue
    intNew = 0
    regscaleIssueUrl = domain + "/api/issues/"
    for iss in issuesData:
        # see if Jira ticket already exists
        if iss["jiraId"] == "":
            # create the new JIRA issue
            new_issue = jiraClient.create_issue(
                project=jira_project,
                summary=iss["title"],
                description=iss["description"],
                issuetype={"name": jira_issue_type},
            )
            # log progress
            intNew += 1
            logger.info(
                str(intNew) + ") Issue Created for Regscale Issue # " + str(iss["id"])
            )
            # get the Jira ID
            strJiraId = new_issue.key
            # update the RegScale issue for the Jira link
            iss["jiraId"] = strJiraId
            # update the issue in RegScale
            strUpdateURL = regscaleIssueUrl + str(iss["id"])
            try:
                requests.request("PUT", strUpdateURL, headers=updateHeaders, json=iss)
                logger.info(
                    str(intNew)
                    + ") Regscale Issue # "
                    + str(iss["id"])
                    + " was updated with the Jira link."
                )
            except requests.exceptions.RequestException as e:
                logger.error(e)

    # output the final result
    logger.info(str(intNew) + " new issue tickets opened in Jira.")
