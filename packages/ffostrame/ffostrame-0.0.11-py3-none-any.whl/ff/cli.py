#!/usr/bin/env python
import rich_click as click
from click_shell import shell

click.rich_click.OPTION_GROUPS = {
    "mytool": [
        {
            "name": "Simple options",
            "options": ["--name", "--description", "--version", "--help"],
        },
        {
            "name": "Advanced options",
            "options": ["--force", "--yes", "--delete"],
        },
    ]
}


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    version_file = open("version.txt", "r")
    version = version_file.read()
    version_file.close()
    click.echo(version)
    ctx.exit()


@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
@shell(prompt="ff > ", intro="Starting ff...")
@click.pass_context
def ff(ctx):

    print("hi")


if __name__ == "__main__":

    ff()
