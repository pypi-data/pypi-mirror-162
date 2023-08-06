#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

############################################################
# Imports
############################################################
import click

import app.healthcheck as hc
import app.login as lg
############################################################
# Versioning
############################################################
from app._version import __version__
from app.ad import ad
from app.jira import jira
from app.logz import create_logger
from app.migrations import migrations
from app.oscal import get_java, oscal
from app.servicenow import servicenow
from app.wiz import wiz

############################################################
# CLI Command Definitions
############################################################


class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        kwargs["help"] = (
            kwargs.get("help", "") + "Option is mutually exclusive with " + "."
        ).strip()
        logger = create_logger()
        self.logger = logger
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        logger.debug(ctx.__dict__)
        if lg.is_valid():
            logger.debug("valid")
        else:
            prompt = list(ctx.__dict__["params"].keys())[0]
            if prompt == "username":
                self.logger.debug(prompt)
                self.prompt = "Enter your RegScale Password"
            # raise click.UsageError(
            #     "Illegal usage: '"
            #     + str(self.name)b
            #     + "' is mutually exclusive with "
            #     + str(mutex_opt)
            #     + "."
            # )
        # if ctx.params["username"] is None:
        #     self.prompt = "Enter your RegScale Password"

        return super(Mutex, self).handle_parse_result(ctx, opts, args)


logger = create_logger()


@click.group()
def cli():
    pass


# About function
@cli.command()
def about():
    """Provides information about the CLI and its current version."""
    click.echo("RegScale CLI Version: " + __version__)
    click.echo("Author: J. Travis Howerton (thowerton@regscale.com)")
    click.echo("Copyright: RegScale Incorporated")
    click.echo("Website: https://www.regscale.com")
    click.echo("Read the CLI Docs: https://regscale.com/documentation/cli-overview")
    java = get_java()
    if "not found" not in java:
        return click.echo(f"Java: {java}")


# Log into RegScale to get a token
@cli.command()
@click.option(
    "--username",
    hide_input=False,
    help="RegScale User Name",
    prompt="Enter RegScale User Name"
    # cls=Mutex,
)
@click.option(
    "--password",
    hide_input=True,
    help="RegScale Password",
    cls=Mutex,
)
def login(username, password=None):

    """Logs the user into their RegScale instance"""
    if password:
        lg.login(username, password)
    else:
        valid = lg.is_valid()
        if valid:
            logger.info("Already logged in!")


# Check the health of the RegScale Application
@cli.command()
def healthcheck():
    """Monitoring tool to check the health of the RegScale instance"""
    hc.status()


# add OSCAL support
cli.add_command(oscal)

# add Wiz support
cli.add_command(wiz)

# add data migration support
cli.add_command(migrations)

# add Azure Active Directory (AD) support
cli.add_command(ad)

# add ServiceNow support
cli.add_command(servicenow)

# add JIRA support
cli.add_command(jira)


# start function for the CLI
if __name__ == "__main__":
    cli()
