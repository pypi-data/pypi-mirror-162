import importlib.resources as pkg_resources

import click
import pyperclip
from markdown_subtemplate.infrastructure.page import process_variables

from . import templates


# https://click.palletsprojects.com/en/8.1.x/api/#click.version_option
@click.command()
@click.version_option()
@click.argument("package")
@click.argument("language", type=click.Choice(["JavaScript", "Python"], case_sensitive=False))
def run(package, language):
    """Generate a list of installation commands for a package to add to README files."""

    # https://docs.python.org/3.7/library/importlib.html#module-importlib.resources
    # https://stackoverflow.com/a/20885799
    template_name = f"{language.lower()}.md"
    template = pkg_resources.read_text(templates, template_name)

    commands = process_variables(template, {"package": package})

    # click.echo(commands)
    pyperclip.copy(commands)
    click.echo("Copied!")
