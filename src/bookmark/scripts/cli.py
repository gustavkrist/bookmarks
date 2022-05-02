import os
from bookmark.components import App
from rich import print
from bookmark.scripts import (
    add_bookmark,
    del_bookmark,
    list_bookmarks,
    check_file,
    reset_file,
)
import rich_click as click

click.rich_click.STYLE_ERRORS_SUGGESTION = "blue italic"
click.rich_click.ERRORS_SUGGESTION = "Try running the --help flag for more information"
click.rich_click.MAX_WIDTH = 100
# click.rich_click.OPTION_GROUPS = {
#     "bm": [
#         {"open": ["-r"]},
#         # {"name": "Advanced Usage", "options": ["-r", "-h"]},
#     ]
# }
click.rich_click.COMMAND_GROUPS = {
    "bm": [
        {"name": "Dashboard", "commands": ["open"]},
        {"name": "Bookmark management", "commands": ["add", "rm", "list"]},
    ]
}


@click.group(
    invoke_without_command=True,
    options_metavar="<options>",
    subcommand_metavar="<command> <args>",
)
@click.pass_context
@click.option(
    "-r",
    "--reset",
    is_flag=True,
    default=False,
    show_default=True,
    help="Reset bookmark file",
)
@click.option(
    "-h", "--help", is_flag=True, default=False, help="Show this message and exit"
)
def cli(ctx, reset, help):
    """
    Open the bookmark dashboard or manage bookmarks.

    If no options or subcommands are passed, the dashboard is opened.

    You can try using --help at the top level and also for specific subcommands.
    """
    if help:
        click.echo(ctx.get_help())
        ctx.exit()
    if reset:
        reset_file()
        ctx.exit()
    else:
        file_status = check_file()
    if file_status == "empty" and ctx.invoked_subcommand in [None, "open"]:
        click.echo(
            "You have added no bookmarks. To show the bookmark dashboard, add a bookmark first."
        )
        click.echo(ctx.get_help())
        ctx.exit()
    if ctx.invoked_subcommand is None:
        ctx.invoke(open)


@cli.command(options_metavar="<options>")
@click.pass_context
@click.option(
    "-h", "--help", is_flag=True, default=False, help="Show this message and exit"
)
def open(ctx, help):
    """
    Opens the bookmark dashboard
    """
    if help:
        click.echo(ctx.get_help())
        ctx.exit()
    else:
        app = App()
        exit_code = app.run()
        while exit_code != 0:
            if isinstance(exit_code, str):
                os.system(exit_code)
            if exit_code == "exec /bin/zsh":
                exit_code = 0
            else:
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
@click.option(
    "-h", "--help", is_flag=True, default=False, help="Show this message and exit"
)
def add(ctx, name_arg, path_arg, name_opt, path_opt, help):
    """Add bookmark <name> with path <path>"""
    if help:
        click.echo(ctx.get_help())
        ctx.exit()
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
        # click.echo("Please provide both <name> and <path>\n")
        raise click.ClickException("Missing argument <path>")
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
@click.option(
    "-h", "--help", is_flag=True, default=False, help="Show this message and exit"
)
def rm(ctx, name_arg, name_opt, help):
    """Delete bookmark with name <name>"""
    if help:
        click.echo(ctx.get_help())
        ctx.exit()
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


@cli.command(options_metavar="<options>")
@click.pass_context
@click.option(
    "-h", "--help", is_flag=True, default=False, help="Show this message and exit"
)
def list(ctx, help):
    """List all bookmarks"""
    if help:
        click.echo(ctx.get_help())
        ctx.exit()
    print(list_bookmarks())
