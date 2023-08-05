from typing import Optional

import sys

from subprocess import check_output

import os

import click

from dnastack.cli.auth.command import auth
from dnastack.cli.config.commands import config_command_group
from dnastack.cli.collections import collection_command_group
from dnastack.cli.config.context import context_command_group, ContextCommandHandler
from dnastack.cli.data_connect.commands import data_connect_command_group
from dnastack.cli.drs import drs_command_group
from dnastack.alpha.cli.commands import alpha_command_group
from dnastack.cli.helpers.command.decorator import command
from dnastack.cli.helpers.command.spec import ArgumentSpec
from dnastack.cli.helpers.command.group import AliasedGroup
from .constants import __version__

APP_NAME = 'dnastack'


@click.group(APP_NAME, cls=AliasedGroup)
@click.version_option(__version__, message="%(version)s")
def dnastack():
    """
    DNAstack Client CLI

    https://www.dnastack.com
    """


@command(dnastack)
def version():
    """ Show the version of CLI/library """
    library_version = (
        f"{check_output(['git', 'describe', '--abbrev=7']).decode().strip()} (dev)"
        if os.path.exists('.git')
        else __version__
    )
    python_version = str(sys.version).replace("\n", " ")
    click.echo(f'{APP_NAME} {library_version} with Python {python_version}')


@command(dnastack,
         specs=[
             ArgumentSpec(
                 name='context_name',
                 arg_names=['--name'],
                 as_option=True,
                 help='Context name -- default to hostname'
             )
         ])
def use(registry_hostname_or_url: str, context_name: Optional[str] = None, no_auth: bool = False):
    """
    Import a configuration from host's service registry (if available) or the corresponding public configuration from
    cloud storage. If "--no-auth" is not defined, it will automatically initiate all authentication.

    This will also switch the default context to the given hostname.

    This is a shortcut to "dnastack config contexts use".
    """
    ContextCommandHandler().use(registry_hostname_or_url, context_name=context_name, no_auth=no_auth)


# noinspection PyTypeChecker
dnastack.add_command(data_connect_command_group)
# noinspection PyTypeChecker
dnastack.add_command(config_command_group)
# noinspection PyTypeChecker
dnastack.add_command(drs_command_group)
# noinspection PyTypeChecker
dnastack.add_command(auth)
# noinspection PyTypeChecker
dnastack.add_command(collection_command_group)
# noinspection PyTypeChecker
dnastack.add_command(context_command_group)
# noinspection PyTypeChecker
dnastack.add_command(alpha_command_group)

if __name__ == "__main__":
    dnastack.main(prog_name="dnastack")
