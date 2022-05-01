import rich_click as click
import json
import os
from rich import box
from rich.table import Table
from rich.text import Text


def add_bookmark(name, path):
    if os.getenv("BOOKMARK_PATH") is not None:
        bookmark_path = os.getenv("BOOKMARK_PATH")
    else:
        bookmark_path = os.getenv("HOME") + "/.bookmarks"
    with open(bookmark_path, "r") as f:
        json_dict = json.load(f)
    bookmarks = json_dict["bookmarks"]
    bookmarks[name] = path
    with open(bookmark_path, "w") as f:
        json_dict["bookmarks"] = bookmarks
        json.dump(json_dict, f, indent=4, separators=(",", ": "), sort_keys=True)


def del_bookmark(name):
    if os.getenv("BOOKMARK_PATH") is not None:
        bookmark_path = os.getenv("BOOKMARK_PATH")
    else:
        bookmark_path = os.getenv("HOME") + "/.bookmarks"
    with open(bookmark_path, "r") as f:
        json_dict = json.load(f)
        bookmarks = json_dict["bookmarks"]
    try:
        bookmarks.pop(name)
    except KeyError:
        raise click.ClickException("Bookmark is not in bookmark list")
    with open(bookmark_path, "w") as f:
        json_dict["bookmarks"] = bookmarks
        json.dump(json_dict, f, indent=4, separators=(",", ": "), sort_keys=True)


def list_bookmarks():
    if os.getenv("BOOKMARK_PATH") is not None:
        bookmark_path = os.getenv("BOOKMARK_PATH")
    else:
        bookmark_path = os.getenv("HOME") + "/.bookmarks"
    with open(bookmark_path, "r") as f:
        json_dict = json.load(f)
        bookmarks = json_dict["bookmarks"]
    dir_bookmarks = []
    file_bookmarks = []
    for name, path in bookmarks.items():
        if os.path.isdir(path):
            dir_bookmarks.append((name, path))
        else:
            file_bookmarks.append((name, path))
    table = Table(title="Bookmarks", box=box.HEAVY_HEAD, show_lines=True)
    table.add_column("Bookmark name", style="cyan", no_wrap=True)
    table.add_column("Path", style="magenta", no_wrap=True)
    for name, path in sorted(dir_bookmarks):
        table.add_row(Text.from_markup(f":open_file_folder: {name}"), path)
    for name, path in sorted(file_bookmarks):
        table.add_row(Text.from_markup(f":page_facing_up: {name}"), path)
    return table


def ignore_element(bookmark, element):
    if os.getenv("BOOKMARK_PATH") is not None:
        bookmark_path = os.getenv("BOOKMARK_PATH")
    else:
        bookmark_path = os.getenv("HOME") + "/.bookmarks"
    with open(bookmark_path, "r") as f:
        json_dict = json.load(f)
        ignores = json_dict["ignores"]
    try:
        if bookmark in ignores:
            ignores[bookmark].append(element)
        else:
            ignores[bookmark] = [element]
    except KeyError:
        raise click.ClickException("Invalid bookmark provided")
    with open(bookmark_path, "w") as f:
        json_dict["ignores"] = ignores
        json.dump(json_dict, f, indent=4, separators=(",", ": "), sort_keys=True)
