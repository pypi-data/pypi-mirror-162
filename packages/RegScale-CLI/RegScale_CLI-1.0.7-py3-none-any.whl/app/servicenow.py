import json
import os.path

import click
import requests
import yaml

from app.logz import create_logger


# Create group to handle ServiceNow integration
@click.group()
def servicenow():
    """Auto-assigns incidents in ServiceNow for remediation"""
    pass


#####################################################################################################
#
# PROCESS ISSUES TO ServiceNow
# ServiceNow REST API Docs: https://docs.servicenow.com/bundle/paris-application-development/page/build/applications/concept/api-rest.html
# Use the REST API Explorer in ServiceNow to select table, get URL, and select which fields to populate
#
#####################################################################################################
@servicenow.command()
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
    "--snow_assignment_group",
    prompt="Enter the name of the project in Jira",
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
)
@click.option(
    "--snow_incident_type",
    prompt="Enter the ServiceNow incident type",
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale",
)
def issues(
    issue_level, regscale_id, regscale_module, snow_assignment_group, snow_incident_type
):
    """Process issues to ServiceNow"""

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
    strUser = config["userId"]
    snowURL = config["snowUrl"]
    snowUser = config["snowUserName"]
    snowPWD = config["snowPassword"]

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
            logger.error("ERROR: Unable to fetch issues from RegScale")
            quit()

    # make directory if it doesn't exist
    if os.path.exists("./artifacts") is False:
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

    # loop over the issues and write them out
    intNew = 0
    regscaleIssueUrl = config["domain"] + "/api/issues/"
    for iss in issuesData:
        # build the issue URL for cross linking
        strIssueUrl = config["domain"] + "/issues/form/" + str(iss["id"])
        # see if the ServiceNow ticket already exists
        if iss["serviceNowId"] == "":
            # create a new ServiceNow incident
            snowIncident = {
                "description": iss["description"],
                "short_description": iss["title"],
                "assignment_group": snow_assignment_group,
                "due_date": iss["dueDate"],
                "comments": "RegScale Issue #" + str(iss["id"]) + " - " + strIssueUrl,
                "state": "New",
                "urgency": snow_incident_type,
            }

            # create a SNOW incident
            incidentUrl = snowURL + "api/now/table/incident"
            snowHeader = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            try:
                intNew += 1
                response = requests.post(
                    incidentUrl,
                    auth=(snowUser, snowPWD),
                    headers=snowHeader,
                    json=snowIncident,
                )
                snowResponse = response.json()
                # log the result
                logger.info(
                    "SNOW Incident ID" + snowResponse["result"]["sys_id"] + " created"
                )
                # get the SNOW ID
                iss["serviceNowId"] = snowResponse["result"]["sys_id"]
                # update the issue in RegScale
                strUpdateURL = regscaleIssueUrl + str(iss["id"])
                try:
                    requests.request(
                        "PUT", strUpdateURL, headers=updateHeaders, json=iss
                    )
                    logger.info(
                        str(intNew)
                        + ") Regscale Issue # "
                        + str(iss["id"])
                        + " was updated with the ServiceNow link."
                    )
                except requests.exceptions.RequestException as e:
                    # problem updating RegScale
                    logger.info(e)
            except requests.exceptions.RequestException as e:
                # problem creating in ServiceNow
                logger.info(e)

    # output the final result
    logger.info(str(intNew) + " new issue incidents opened in ServiceNow.")
