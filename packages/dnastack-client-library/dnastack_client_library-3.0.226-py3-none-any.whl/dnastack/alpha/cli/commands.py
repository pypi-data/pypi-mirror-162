import click

from dnastack.alpha.cli.auth import alpha_auth_command_group
from dnastack.alpha.cli.wes import alpha_wes_command_group
from dnastack.cli.helpers.printer import echo_header
from dnastack.feature_flags import dev_mode, in_interactive_shell


@click.group("alpha", hidden=not dev_mode)
def alpha_command_group():
    """
    Interact with testing/unstable/experimental commands.

    Warning: Alpha commands are experimental. This command may change incompatibly.
    """

    if dev_mode or not in_interactive_shell:
        return

    echo_header("Warning: Alpha commands are experimental. This command may change incompatibly.",
                bg='yellow',
                fg='black',
                bold=False,
                err=True,
                top_margin=0,
                bottom_margin=0)


alpha_command_group.add_command(alpha_auth_command_group)
alpha_command_group.add_command(alpha_wes_command_group)