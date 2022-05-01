import os
from components import App
from rich import print
from util import add_bookmark, del_bookmark, list_bookmarks
import click
import pickle


@click.group(invoke_without_command=True)
@click.pass_context
# @click.option(
#     "-r",
#     "--restart",
#     is_flag=True,
#     default=False,
#     show_default=True,
#     help="Start a fresh instance",
# )
def cli(ctx):
    if ctx.invoked_subcommand is None:
        """Opens the bookmark dashboard"""
        app = App()
        exit_code = app.run()
        while exit_code != 0:
            if isinstance(exit_code, str):
                os.system(exit_code)
            exit_code = app.run(init=False)


@cli.command(options_metavar="<options>")
@click.pass_context
@click.argument(
    "name_arg",
    required=False,
    metavar="<name>",
    type=click.STRING,
)
@click.argument(
    "path_arg",
    required=False,
    metavar="<path>",
    type=click.Path(exists=True, resolve_path=True),
)
@click.option(
    "-n",
    "--name",
    "name_opt",
    metavar="<name>",
    help="Name of bookmark to add",
    type=click.STRING,
)
@click.option(
    "-p",
    "--path",
    "path_opt",
    metavar="<path>",
    help="Path for the bookmark to point to",
    type=click.Path(exists=True, resolve_path=True),
)
def add(ctx, name_arg, path_arg, name_opt, path_opt):
    """Add bookmark <name> with path <path>"""
    if None not in (name_arg, name_opt):
        raise click.ClickException(
            "<name> positional argument and -n <name> option are mutually exclusive"
        )
    if None not in (path_arg, path_opt):
        raise click.ClickException(
            "<path> positional argument and -p <path> option are mutually exclusive"
        )
    if name_arg is None and name_opt is None:
        if path_opt is None:
            click.echo(ctx.get_help())
            ctx.exit()
        else:
            path = path_opt
            click.echo("Missing bookmark name")
            name = input("Bookmark name: ")
    elif path_arg is None and path_opt is None:
        click.echo("Please provide both <name> and <path>\n")
        click.echo(ctx.get_help())
        ctx.exit()
    name = name_arg if name_opt is None else name_opt
    path = path_arg if path_opt is None else path_opt
    add_bookmark(name, path)


@cli.command(options_metavar="<options>")
@click.pass_context
@click.argument(
    "name_arg",
    required=False,
    metavar="<name>",
    type=click.STRING,
)
@click.option(
    "-n",
    "--name",
    "name_opt",
    metavar="<name>",
    help="Name of bookmark to add",
    type=click.STRING,
)
def rm(ctx, name_arg, name_opt):
    """Delete bookmark with name <name>"""
    if None not in (name_arg, name_opt):
        raise click.ClickException(
            "<name> positional argument and -n <name> option are mutually exclusive"
        )
    if name_arg is None and name_opt is None:
        click.echo("Missing bookmark name\n")
        click.echo(ctx.get_help())
        ctx.exit()
    name = name_arg if name_opt is None else name_opt
    del_bookmark(name)


@cli.command()
def list():
    """List all bookmarks"""
    print(list_bookmarks())
