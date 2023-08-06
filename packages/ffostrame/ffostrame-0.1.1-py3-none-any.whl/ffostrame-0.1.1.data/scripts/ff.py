#!python

from tkinter import W
import get

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


@shell(prompt="ff > ", intro="Starting ff...")
@click.pass_context
def cli(ctx):

    #TODO: Pass something if needed in near future
    ctx.obj = {}

cli.add_command(get.get)

if __name__ == "__main__":

    cli()
