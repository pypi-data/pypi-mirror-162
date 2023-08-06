#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

import json
import os
from socket import timeout
import uuid
from pathlib import Path
from subprocess import PIPE, STDOUT, CalledProcessError, Popen, run

import click
import requests
from requests.adapters import HTTPAdapter, Retry

import yaml

from app.application import Application
from app.logz import create_logger

logger = create_logger()
config = Application().config
oscal_location = Path(config["oscal_location"])
saxon_path = Path(config["saxon_path"])

s = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
s.mount("https://", HTTPAdapter(max_retries=retries))

# Create group to handle OSCAL processing
@click.group()
def oscal():
    """Performs bulk processing of OSCAL files"""
    pass


# OSCAL Version Support
@oscal.command()
def version():
    """Info on current OSCAL version supported by RegScale"""
    logger.info("RegScale currently supports OSCAL Version 1.0")


# Convert OSCAL formatted catalog json file to OSCAL xml
@oscal.command(name="convert-catalog-json-xml")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
# TODO: Profile to XML
# TODO: SSP to XML
def convert_catalog_json_xml(
    input,
    output,
    xsl_file=f"{str(oscal_location.absolute())}{os.sep}xml{os.sep}convert{os.sep}oscal_catalog_json-to-xml-converter.xsl",
):
    """Convert Catalog from XML to JSON (Current Folder)

    Provide INPUT filename

    Provide OUTPUT filename

    ex. regscale oscal convert-catalog-json-xml /data/basic-catalog.json /tmp/output.xml
    \f
    """
    convert(xsl=xsl_file, input=input, output=output, mode="from-json")


# Convert OSCAL formatted ssp json file to OSCAL xml
@oscal.command(name="convert-ssp-json-xml")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
# TODO: Profile to XML
# TODO: SSP to XML
def convert_ssp_json_xml(
    input,
    output,
    xsl_file=f"{str(oscal_location.absolute())}{os.sep}xml{os.sep}convert{os.sep}oscal_ssp_json-to-xml-converter.xsl",
):
    """Convert SSP from XML to JSON (Current Folder)

    Provide INPUT filename

    Provide OUTPUT filename

    ex. regscale oscal convert-ssp-json-xml /data/basic-ssp.json /tmp/output.xml
    \f
    """
    convert(xsl=xsl_file, input=input, output=output, mode="from-json")


@oscal.command(name="convert-json-yaml")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def convert_json_yaml(input: str, output: str):
    """Convert JSON to YAML

    Args:
        input (str): XML input path as string
        output (str): YAML output path as string
    """
    input_path = Path(input)
    output_path = Path(output)
    with open(input_path, "r") as json_in, open(output_path, "w") as yaml_out:
        try:
            json_payload = json.load(json_in)
            yaml.dump(json_payload, yaml_out, sort_keys=False, encoding="utf-8")
            logger.info(
                f"finished exporting {str(input_path.absolute())} to {str(output_path.absolute())}!"
            )
        except json.JSONDecodeError as e:
            logger.error("JSON Decode ERROR: %s", e)
            quit()


def convert(xsl, input: str, output: str, mode: str):
    """Convert XML to JSON using an XSL file (Current Folder)

    Provide INPUT filename

    Provide OUTPUT filename

    ex. regscale oscal convert-ssp-json-xml /data/basic-ssp.json /tmp/output.xml
    \f
    """

    logger.debug(Path(input))
    assert Path(input).exists()
    input_path = str(Path(input).absolute())
    if "unable to access jarfile".lower() in get_java() or not saxon_path.exists():
        logger.error("Saxon Jar(s) not found, please make Saxon jarfiles available")

    elif "not found" not in get_java():
        if saxon_path.exists():
            logger.debug(xsl)
            command = [
                "java",
                "-jar",
                f"{saxon_path}",  # TODO: Make this path work with windows
                f"-xsl:{xsl}",
                f"-o:{output}",  # TODO: Make this path work with windows
                f"-it:{mode}",
                f"file={input_path}",  # TODO: Make this path work with windows
            ]
            logger.info(
                "Executing OSCAL Conversion... %s",
                [" ".join([str(item) for item in command])],
            )
            try:
                run([" ".join([str(item) for item in command])], shell=True, check=True)
                logger.info(f"finished!  Output file saved: {output}")
            except CalledProcessError as e:
                logger.error("CalledProcessError: %s", e)
            # TODO Add OSCAL validation step
    else:
        logger.warning(
            "Java distribution not found, Java is required to execute OSCAL conversion tools"
        )


def get_java() -> str:
    """
    Get Java Version from system
    Returns:
        str: Java Version
    """
    command = "java --version"
    p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    out = iter(p.stdout.readline, b"")
    return list(out)[0].decode("utf-8").rstrip("\n")


# OSCAL Profile Loader Support
@oscal.command()
@click.option(
    "--title",
    prompt="Enter the title for the OSCAL profile",
    help="RegScale will name the profile with the title provided",
)
@click.option(
    "--categorization",
    prompt="Enter the FIPS categorization level",
    help="Choose from Low, Moderate, or High",
)
@click.option(
    "--catalog",
    prompt="Enter the RegScale Catalog ID to use",
    help="Primary key (unique ID) of the RegScale catalog",
)
@click.option(
    "--file_name",
    prompt="Enter the file name of the OSCAL profile to process",
    help="RegScale will process and load the profile along with all specified controls",
)
def profile(title, categorization, catalog, file_name):
    """OSCAL Profile Loader

    Args:
        title (_type_): _description_
        categorization (_type_): _description_
        catalog (_type_): _description_
        file_name (_type_): _description_
    """
    # validation
    if file_name == "":
        logger.error("No file name provided.")
        quit()
    elif title == "":
        logger.error("No title provided for this RegScale profile.")
        quit()
    elif int(catalog) <= 0:
        logger.error("No catalog provided or catalog invalid.")
        quit()
    elif (
        categorization != "Low"
        and categorization != "Moderate"
        and categorization != "High"
    ):
        logger.error("Categorization not provided or invalid.")
        quit()
    else:
        # load the catalog
        try:
            oscal = open(file_name, "r", encoding="utf-8-sig")
            oscalData = json.load(oscal)
        except:
            logger.error("Unable to open the specified OSCAL file for processing.")
            quit()

        # load the config from YAML
        try:
            with open("init.yaml", "r") as stream:
                config = yaml.safe_load(stream)
        except:
            logger.error("Unable to open the init file.")
            quit()

        # set headers
        strUser = config["userId"]
        headers = {"Accept": "application/json", "Authorization": config["token"]}

        # create a new profile
        profile = {
            "id": 0,
            "uuid": "",
            "name": title,
            "confidentiality": "",
            "integrity": "",
            "availability": "",
            "category": categorization,
            "profileOwnerId": strUser,
            "createdById": strUser,
            "dateCreated": None,
            "lastUpdatedById": strUser,
            "dateLastUpdated": None,
            "isPublic": True,
        }

        # create the profile
        url_prof = config["domain"] + "/api/profiles/"
        logger.info("RegScale creating a new profile....")
        try:
            profResponse = s.post(url=url_prof, headers=headers, json=profile)
            profJsonResponse = profResponse.json()
            logger.info("\nProfile ID: " + str(profJsonResponse["id"]))
            # get the catalog ID
            intProfile = profJsonResponse["id"]
        except:
            logger.error("Unable to create profile in RegScale")
            quit()

        # get the list of existing controls for the catalog
        url_sc = config["domain"] + "/api/SecurityControls/getList/" + str(catalog)
        try:
            scResponse = s.get(url_sc, headers=headers)
            scData = scResponse.json()
        except:
            logger.error(
                "Unable to retrieve security controls for this catalog in RegScale"
            )
            quit()

        # loop through each item in the OSCAL control set
        mappings = []
        for m in oscalData["profile"]["imports"][0]["include-controls"][0]["with-ids"]:
            bMatch = False
            for sc in scData:
                if m == sc["controlId"]:
                    bMatch = True
                    map = {"id": 0, "profileID": intProfile, "controlID": int(sc["id"])}
                    mappings.append(map)
                    break
            if bMatch == False:
                logger.error("Unable to locate control: " + m)

        # upload the controls to the profile as mappings
        url_maps = config["domain"] + "/api/profileMapping/batchCreate"
        try:
            mapResponse = s.post(url_maps, headers=headers, json=mappings)
            mapData = mapResponse.json()
            logger.info(
                str(len(mappings))
                + " total mappings created in RegScale for this profile."
            )
        except:
            logger.error("Unable to create mappings for this catalog in RegScale")
            quit()


# Process catalog from OSCAL
@oscal.command()
@click.option(
    "--file_name",
    prompt="Enter the file name of the NIST Catalog to process",
    help="RegScale will process and load the catalog along with all controls, statements, and parameters",
)
def catalog(file_name):
    """Process and load catalog to RegScale"""

    # validation of file name
    if file_name == "":
        logger.error("No file name provided.")
        quit()
    else:
        # load the catalog
        try:
            oscal_file_data = open(file_name, "r", encoding="utf-8-sig")
            oscalData = json.load(oscal_file_data)
        except Exception:
            logger.error("Unable to open the specified OSCAL file for processing.")
            quit()

    # load the config from YAML
    try:
        with open("init.yaml", "r") as stream:
            config = yaml.safe_load(stream)
    except Exception:
        logger.error("Unable to open the init file.")
        quit()

    # debug flag to pause upload when testing and debugging (always true for production CLI use)
    bUpload = True
    bParams = True
    bTests = True
    bOBJs = True
    bDeepLinks = True

    # set headers
    strUser = config["userId"]
    headers = {"Accept": "application/json", "Authorization": config["token"]}

    # parse the OSCAL JSON to get related data (used to enrich base spreadsheet)
    arrL1 = oscalData["catalog"]
    strUUID = arrL1["uuid"]

    # process resources for lookup
    resources = []
    arrL2 = arrL1["back-matter"]
    for i in arrL2["resources"]:
        # make sure values exist
        strResourceTitle = ""
        if "title" in i:
            strResourceTitle = i["title"]
        strResourceGUID = ""
        if "uuid" in i:
            strResourceGUID = i["uuid"]
        strCitation = ""
        if "citation" in i:
            citation = i["citation"]
            if "text" in citation:
                strCitation = citation["text"]
        strLinks = ""
        if "rlinks" in i:
            links = i["rlinks"]
            for x in links:
                if "href" in x:
                    strLinks += x["href"] + "<br/>"
        # add parsed/flattened resource to the array
        res = {
            "uuid": strResourceGUID,
            "short": strResourceTitle,
            "title": strCitation,
            "links": strLinks,
        }
        resources.append(res)

    # Write to file to visualize the output
    with open("processing/resources.json", "w") as outfile:
        outfile.write(json.dumps(resources, indent=4))

    # create the resource table
    strResources = ""
    strResources += '<table border="1" style="width: 100%;"><tr style="font-weight: bold"><td>UUID</td><td>Title</td><td>Links</td></tr>'
    for res in resources:
        strResources += "<tr>"
        strResources += "<td>" + res["uuid"] + "</td>"
        strResources += "<td>" + res["title"] + "</td>"
        strResources += "<td>" + res["links"] + "</td>"
        strResources += "</tr>"
    strResources += "</table>"

    # set the catalog URL for your Atlasity instance
    url_cats = config["domain"] + "/api/catalogues/"

    # setup catalog data
    cat = {
        "title": arrL1["metadata"]["title"],
        "description": "This publication provides a catalog of security and privacy controls for information systems and organizations to protect organizational operations and assets, individuals, other organizations, and the Nation from a diverse set of threats and risks, including hostile attacks, human errors, natural disasters, structural failures, foreign intelligence entities, and privacy risks. <br/><br/><strong>Resources</strong><br/><br/>"
        + strResources,
        "datePublished": arrL1["metadata"]["version"],
        "uuid": strUUID,
        "lastRevisionDate": arrL1["metadata"]["version"],
        "url": "https://csrc.nist.gov/",
        "abstract": "This publication provides a catalog of security and privacy controls for federal information systems and organizations and a process for selecting controls to protect organizational operations (including mission, functions, image, and reputation), organizational assets, individuals, other organizations, and the Nation from a diverse set of threats including hostile cyber attacks, natural disasters, structural failures, and human errors (both intentional and unintentional). The security and privacy controls are customizable and implemented as part of an organization-wide process that manages information security and privacy risk. The controls address a diverse set of security and privacy requirements across the federal government and critical infrastructure, derived from legislation, Executive Orders, policies, directives, regulations, standards, and/or mission/business needs. The publication also describes how to develop specialized sets of controls, or overlays, tailored for specific types of missions/business functions, technologies, or environments of operation. Finally, the catalog of security controls addresses security from both a functionality perspective (the strength of security functions and mechanisms provided) and an assurance perspective (the measures of confidence in the implemented security capability). Addressing both security functionality and assurance helps to ensure that information technology component products and the information systems built from those products using sound system and security engineering principles are sufficiently trustworthy.",
        "keywords": "FIPS Publication 200; FISMA; Privacy Act; Risk Management Framework; security controls; FIPS Publication 199; security requirements; computer security; assurance;",
        "createdById": strUser,
        "lastUpdatedById": strUser,
    }

    # create the catalog and print success result
    if bUpload == True:
        logger.info("RegScale creating catalog....")
        try:
            response = s.post(url=url_cats, headers=headers, json=cat)
            # response = requests.request(url=url_cats, headers=headers, json=cat)
            jsonResponse = response.json()
            logger.info("\nCatalog ID: " + str(jsonResponse["id"]))
            # get the catalog ID
            intCat = jsonResponse["id"]
        except Exception:
            logger.error("Unable to create catalog in RegScale")
            quit()
    else:
        # don't set ID in debug mode
        intCat = 0

    # process NIST families of controls
    families = []
    oscalControls = []
    parameters = []
    parts = []
    assessments = []

    # process groups of controls
    for i in arrL1["groups"]:
        strFamily = i["title"]
        f = {
            "id": i["id"],
            "title": i["title"],
        }
        # add parsed item to the family array
        families.append(f)

        # loop through controls
        for ctrl in i["controls"]:

            # process the control
            newCTRL = processControl(
                ctrl, resources, strFamily, parameters, parts, assessments
            )
            oscalControls.append(newCTRL)

            # check for child controls/enhancements
            if "controls" in ctrl:
                childCTRLs = ctrl["controls"]
                for childCTRL in childCTRLs:
                    child = processControl(
                        childCTRL, resources, strFamily, parameters, parts, assessments
                    )
                    oscalControls.append(child)

    # # Write to file to visualize the output
    with open("processing/families.json", "w") as outfile:
        outfile.write(json.dumps(families, indent=4))
    logger.info(str(len(families)) + " total families processed.")

    # # Write to file to visualize the output
    with open("processing/controls.json", "w") as outfile:
        outfile.write(json.dumps(oscalControls, indent=4))
    logger.info(str(len(oscalControls)) + " total controls processed.")

    # # Write to file to visualize the output
    with open("processing/parameters.json", "w") as outfile:
        outfile.write(json.dumps(parameters, indent=4))
    logger.info(str(len(parameters)) + " total parameters processed.")

    # # Write to file to visualize the output
    with open("processing/parts.json", "w") as outfile:
        outfile.write(json.dumps(parts, indent=4))
    logger.info(str(len(parts)) + " total parts processed.")

    # # Write to file to visualize the output
    with open("processing/tests.json", "w") as outfile:
        outfile.write(json.dumps(assessments, indent=4))
    logger.info(str(len(assessments)) + " total assessments processed.")

    # create controls array
    controls = []
    newControls = []
    errors = []

    # create a counter for records created
    intTotal = 0

    # RegScale URLs
    url_sc = config["domain"] + "/api/securitycontrols/"
    url_params = config["domain"] + "/api/controlParameters/"
    url_tests = config["domain"] + "/api/controlTestPlans/"
    url_objs = config["domain"] + "/api/controlObjectives/"

    # loop through and print the results
    for i in oscalControls:

        # create each security control
        sc = {
            "title": i["id"] + " - " + i["title"],
            "controlType": "Stand-Alone",
            "controlId": i["id"],
            "description": i["parts"] + "<br/><br/>" + i["guidance"],
            "references": i["links"],
            "relatedControls": "",
            "subControls": "",
            "enhancements": i["enhancements"],
            "family": i["family"],
            "mappings": i["parameters"],
            "assessmentPlan": i["assessment"],
            "weight": 0,
            "practiceLevel": "",
            "catalogueID": intCat,
            "createdById": strUser,
            "lastUpdatedById": strUser,
        }

        # append the result
        controls.append(sc)

        # attempt to create the security control
        if bUpload == True:
            try:
                # upload to RegScale
                response = s.post(url=url_sc, headers=headers, json=sc)
                jsonResponse = response.json()
                logger.info("\n\nSuccess - " + sc["title"])
                intTotal += 1

                # add the new controls
                newControls.append(jsonResponse)
            except Exception:
                logger.error("Unable to create security control: " + sc["title"])
                errors.append(sc)

    # Write to file to visualize the output
    with open("processing/mappedControls.json", "w") as outfile:
        outfile.write(json.dumps(controls, indent=4))

    # Write to file to visualize the output
    if bUpload == True:
        with open("processing/newControls.json", "w") as outfile:
            outfile.write(json.dumps(newControls, indent=4))
    else:
        loadControls = open("processing/newControls.json", "r", encoding="utf-8-sig")
        newControls = json.load(loadControls)

    #############################################################################
    #
    #   Start Processing Child Records of the Controls
    #
    #############################################################################
    # only process if the controls exists to map to
    if len(newControls) > 0:
        # load the parameters
        newParams = []
        for p in parameters:
            # find the parent control
            ctrlLookup = next(
                (item for item in newControls if (item["controlId"] == p["controlId"])),
                None,
            )
            if ctrlLookup == None:
                logger.error(
                    "Error: Unable to locate "
                    + p["controlId"]
                    + " for this parameter: "
                    + p["name"]
                )
            else:
                # create a new parameter to upload
                newParam = {
                    "id": 0,
                    "uuid": "",
                    "text": p["value"],
                    "dataType": "string",
                    "parameterId": p["name"],
                    "securityControlId": ctrlLookup["id"],
                    "archived": False,
                    "createdById": strUser,
                    "dateCreated": None,
                    "lastUpdatedById": strUser,
                    "dateLastUpdated": None,
                }

                # add the control to the new array
                newParams.append(newParam)

                # attempt to create the parameter
                if bParams == True:
                    try:
                        # upload to RegScale
                        response = s.post(url_params, headers=headers, json=newParam)
                        jsonResponse = response.json()
                        logger.info(
                            "\n\nSuccess - "
                            + newParam["parameterId"]
                            + " parameter uploaded successfully."
                        )
                    except Exception:
                        logger.error(
                            "Unable to create parameter: " + newParam["parameterId"]
                        )
                        errors.append(newParam)

        # output the result
        with open("processing/newParameters.json", "w") as outfile:
            outfile.write(json.dumps(newParams, indent=4))

        # load the tests
        newTests = []
        for ast in assessments:
            # find the parent control
            ctrlLookup = next(
                (
                    item
                    for item in newControls
                    if (item["controlId"] == ast["parentControl"])
                ),
                None,
            )
            if ctrlLookup == None:
                logger.error(
                    "Error: Unable to locate "
                    + ast["parentControl"]
                    + " for this test: "
                )
            else:
                # create a new test to upload
                newTest = {
                    "id": 0,
                    "uuid": "",
                    "test": ast["testType"] + " - " + ast["description"],
                    "testId": str(uuid.uuid4()),
                    "securityControlId": ctrlLookup["id"],
                    "archived": False,
                    "createdById": strUser,
                    "dateCreated": None,
                    "lastUpdatedById": strUser,
                    "dateLastUpdated": None,
                }

                # add the test to the new array
                newTests.append(newTest)

                # attempt to create the test
                if bTests == True:
                    try:
                        # upload to RegScale
                        response = s.post(url_tests, headers=headers, json=newTest)
                        jsonResponse = response.json()
                        logger.info(
                            "\n\nSuccess - "
                            + newTest["test"]
                            + " -  test uploaded successfully."
                        )
                    except Exception:
                        logger.error("Unable to create test: " + newTest["test"])
                        errors.append(newTest)

        # output the result
        with open("processing/newTests.json", "w") as outfile:
            outfile.write(json.dumps(newTests, indent=4))

        # load the objectives/parts
        newObjectives = []
        for p in parts:
            # find the parent control
            ctrlLookup = next(
                (
                    item
                    for item in newControls
                    if (item["controlId"] == p["parentControl"])
                ),
                None,
            )
            if ctrlLookup == None:
                logger.error(
                    "Error: Unable to locate "
                    + p["parentControl"]
                    + " for this objective/part: "
                    + p["name"]
                )
            else:
                # create a new test to upload
                newObj = {
                    "id": 0,
                    "uuid": "",
                    "name": p["name"],
                    "description": p["description"],
                    "objectiveType": p["objectiveType"],
                    "otherId": "",
                    "securityControlId": ctrlLookup["id"],
                    "parentObjectiveId": None,
                    "archived": False,
                    "createdById": strUser,
                    "dateCreated": None,
                    "lastUpdatedById": strUser,
                    "dateLastUpdated": None,
                }

                # add the part to the new array
                newObjectives.append(newObj)

                # attempt to create the objective
                if bOBJs == True:
                    try:
                        # upload to RegScale
                        response = s.post(url_objs, headers=headers, json=newObj)
                        jsonResponse = response.json()
                        logger.info(
                            "\n\nSuccess - "
                            + newObj["name"]
                            + " -  objective uploaded successfully."
                        )
                    except Exception:
                        logger.error("Unable to create objective: " + newObj["name"])
                        errors.append(newObj)

        # process deep links
        if bDeepLinks == True:
            # get the list from RegScale
            try:
                logger.info(
                    "Retrieving all objectives for this catalogue #"
                    + str(intCat)
                    + " from RegScale (this might take a minute)..."
                )
                url_deep = (
                    config["domain"]
                    + "/api/controlObjectives/getByCatalogue/"
                    + str(intCat)
                )
                objListResponse = s.get(url_deep, headers=headers)
                objList = objListResponse.json()
                logger.info(
                    str(len(objList))
                    + " total objectives now retrieved from RegScale for processing."
                )
            except Exception:
                logger.error(
                    "ERROR: Unable to retrieve control objective information from RegScale."
                )
                quit()

            # loop through each objective and see if it has a parent, if so, update parent ID and send update to RegScale
            intUpdates = 0
            for objReg in objList:
                # find the part by name
                partLookup = next(
                    (item for item in parts if (item["name"] == objReg["name"])), None
                )
                if partLookup != None:
                    # see if the part has a parent
                    if partLookup["parentObjective"] != "":
                        logger.info("Found: " + partLookup["parentObjective"])
                        intUpdates += 1
                        # lookup the parent objective from RegScale
                        parentLookup = next(
                            (
                                item
                                for item in objList
                                if (item["name"] == partLookup["parentObjective"])
                            ),
                            None,
                        )
                        if parentLookup != None:
                            logger.info("Found Parent: " + parentLookup["name"])
                            # update the parent
                            updateParent = parentLookup["objective"]
                            updateParent["parentObjectiveId"] = parentLookup["id"]
                            try:
                                # upload to RegScale
                                updateResponse = s.put(
                                    (url_objs + str(updateParent["id"])),
                                    headers=headers,
                                    json=updateParent,
                                )
                                # updateData = updateResponse.json()
                                logger.info(
                                    "Success - "
                                    + updateParent["name"]
                                    + " -  objective parent updated successfully."
                                )
                            except Exception:
                                logger.error(
                                    "Unable to update parent objective: "
                                    + updateParent["name"]
                                )
                                errors.append(newObj)

            logger.info(str(intUpdates) + " total updates found.")

        # output the result
        with open("processing/newObjectives.json", "w") as outfile:
            outfile.write(json.dumps(newObjectives, indent=4))

        # output the errors
        with open("processing/errors.json", "w") as outfile:
            outfile.write(json.dumps(errors, indent=4))


#############################################################################
#
#   Supporting Functions
#
#############################################################################

# function for recursively working through objectives
def processObjectives(obj, parts, ctrl, parentId):
    strOBJ = "<ul>"
    # loop through parts/objectives recursively
    for o in obj:
        # check prose
        strProse = ""
        if "prose" in o:
            strProse = o["prose"]

        # check name
        strName = ""
        if "name" in o:
            strName = o["name"]

        # create the new part
        part = {
            "id": 0,
            "name": o["id"],
            "objectiveType": strName,
            "description": strProse,
            "parentControl": ctrl["id"],
            "parentObjective": parentId,
        }
        parts.append(part)
        strOBJ += "<li>{{" + o["id"] + "}}"
        if "prose" in o:
            strOBJ += " - " + strProse
        strOBJ += "</li>"
        if "parts" in o:
            strOBJ += processObjectives(o["parts"], parts, ctrl, o["id"])
    strOBJ += "</ul>"
    return strOBJ


# function to process each control
def processControl(ctrl, resources, strFamily, parameters, parts, assessments):
    # see if parameters exist
    if "params" in ctrl:
        # loop through each parameter
        for p in ctrl["params"]:
            # create a new parameter object
            pNew = {
                "name": p["id"],
                "value": "",
                "paramType": "",
                "controlId": ctrl["id"],
            }
            # process basic label
            if "label" in p:
                pNew["paramType"] = "text"
                pNew["value"] = p["label"]
            else:
                # initialize
                strParams = "Select ("
                # process select types
                if "select" in p:
                    select = p["select"]
                    if "how-many" in select:
                        strParams += select["how-many"]
                        pNew["paramType"] = "how-many"
                    if "choice" in select:
                        pNew["paramType"] = "choice"
                        strParams += "select) - "
                        for z in select["choice"]:
                            strParams += z + ", "
                    pNew["value"] = strParams
            # add to the array
            parameters.append(pNew)

    # get enhancements
    strEnhance = ""
    if "controls" in ctrl:
        childENHC = ctrl["controls"]
        strEnhance += "<strong>Enhancements</strong><br/><br/>"
        strEnhance += "<ul>"
        for che in childENHC:
            strEnhance += "<li>{{" + che["id"] + "}} - " + che["title"] + "</li>"
        strEnhance += "</ul>"

    # process control links
    intLinks = 1
    strLinks = ""
    if "links" in ctrl:
        for l in ctrl["links"]:
            # lookup the OSCAL control to enrich the data
            linkLookup = next(
                (item for item in resources if ("#" + item["uuid"]) == l["href"]), None
            )
            if linkLookup != None:
                strLinks += (
                    str(intLinks)
                    + ") "
                    + linkLookup["title"]
                    + " (OSCAL ID: "
                    + linkLookup["uuid"]
                    + ")<br/>"
                )
                intLinks += 1
            else:
                strLinks += l["href"] + "<br/>"

    # process parts
    partInfo = ProcessParts(ctrl, parts, assessments)

    # add control
    newCTRL = {
        "id": ctrl["id"],
        "title": ctrl["title"],
        "family": strFamily,
        "links": strLinks,
        "parameters": "",
        "parts": partInfo["parts"],
        "assessment": partInfo["assessments"],
        "guidance": partInfo["guidance"],
        "enhancements": strEnhance,
    }

    # return the result
    return newCTRL


def ProcessParts(ctrl, parts, assessments):
    # process parts
    if "parts" in ctrl:
        # initialize
        strParts = ""
        strGuidance = ""
        strAssessment = ""

        # create text field for human display
        strParts += "<ul>"
        for p in ctrl["parts"]:
            if ("id" in p) and (p["name"].startswith("assessment") == False):
                # check prose
                strProse = ""
                if "prose" in p:
                    strProse = p["prose"]

                # check name
                strName = ""
                if "name" in p:
                    strName = p["name"]

                # create the new part
                part = {
                    "id": 0,
                    "name": p["id"],
                    "objectiveType": strName,
                    "description": strProse,
                    "parentControl": ctrl["id"],
                    "parentObjective": "",
                }
                parts.append(part)
                # process objectives
                if (
                    p["name"] == "objective"
                    or p["name"] == "statement"
                    or p["name"] == "item"
                ):
                    try:
                        strParts += "<li>{{" + p["id"] + "}} - " + strProse + "</li>"
                    except Exception:
                        logger.error("Unable to parse part - " + str(p["id"]))
                    if "parts" in p:
                        strParts += processObjectives(p["parts"], parts, ctrl, p["id"])
                # process guidance
                if p["name"] == "guidance":
                    strGuidance = "<ul><li>Guidance</li>"
                    if "prose" in p:
                        strGuidance += "<ul>"
                        strGuidance += "<li>" + p["prose"] + "</li>"
                        strGuidance += "</ul>"
                    if "links" in p:
                        strGuidance += "<ul>"
                        for lkp in p["links"]:
                            strGuidance += (
                                "<li>" + lkp["href"] + ", " + lkp["rel"] + "</li>"
                            )
                        strGuidance += "</ul>"
                    strGuidance += "</ul>"
            else:
                # process assessments
                ProcessAssessments(p, ctrl, assessments)

        strParts += "</ul>"
    else:
        # no parts - set default values
        strParts = ""
        strGuidance = ""
        strAssessment = ""

    # retun the result
    partInfo = {
        "parts": strParts,
        "guidance": strGuidance,
        "assessments": strAssessment,
    }
    return partInfo


# process assessment data
def ProcessAssessments(p, ctrl, assessments):
    # process assessments
    if p["name"].startswith("assessment") == True:
        # see if a lowe level objective that has prose
        if "prose" in p:
            # create new assessment objective
            ast = {
                "id": 0,
                "name": p["id"],
                "testType": p["name"],
                "description": p["prose"],
                "parentControl": ctrl["id"],
            }

            # see if it has any child tests
            if "parts" in p:
                if len(p["parts"]) > 0:
                    for item in p["parts"]:
                        ProcessAssessments(item, ctrl, assessments)
        else:
            # check the id
            strPartID = ""
            if "id" in p:
                strPartID = p["id"]
            else:
                strPartID = str(uuid.uuid4())

            # handle methods
            ast = {
                "id": 0,
                "name": strPartID,
                "testType": "",
                "description": "",
                "parentControl": ctrl["id"],
            }
            if "props" in p:
                if len(p["props"]) > 0:
                    if "value" in p["props"][0]:
                        ast["testType"] = p["props"][0]["value"]
            if "parts" in p:
                if len(p["parts"]) > 0:
                    if "prose" in p["parts"][0]:
                        ast["description"] = p["parts"][0]["prose"]

        # add test of the array
        if ast["description"] != "":
            assessments.append(ast)
