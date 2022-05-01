import os
from getkey import platform, keys
from rich.layout import Layout
from rich.live import Live
from rich.console import Console
from .widgets import ScrollPanel, BookmarkTree


suppress = platform(interrupts={})
getkey = suppress.getkey


class App:
    def setup(self):
        self.console = Console(record=True)
        layout = Layout()
        layout.split_row(
            Layout(ratio=2, name="left"),
            Layout(
                ScrollPanel("", border_style="blue", title="Preview", app=self),
                ratio=3,
                name="preview",
            ),
        )
        layout["left"].split_column(
            Layout(name="bookmarks"),
            Layout(
                ScrollPanel(
                    "", border_style="blue", title="Directory Overview", app=self
                ),
                name="directory",
            ),
        )
        bookmarks = BookmarkTree("Bookmarks", style="cyan", app=self)
        if os.getenv("BOOKMARK_PATH") is not None:
            bookmarks.load_file(f"{os.getenv('BOOKMARK_PATH')}")
        else:
            bookmarks.load_file(f"{os.getenv('HOME')}/.bookmarks")
        layout["bookmarks"].update(
            ScrollPanel(bookmarks, title="Bookmarks", border_style="Blue", app=self)
        )
        bookmarks.panel = layout["bookmarks"].renderable
        layout["bookmarks"].renderable.layout = layout["bookmarks"]
        layout["directory"].renderable.layout = layout["directory"]
        layout["preview"].renderable.layout = layout["preview"]
        self.bookmarks = bookmarks
        self.layout = layout
        self.bindings = {
            "q": self.stop,
            keys.CTRL_C: self.stop,
            "1": lambda: self.focus("bookmarks"),
            keys.CTRL_K: lambda: self.focus("bookmarks"),
            keys.ESC: lambda: self.focus("bookmarks"),
            "2": lambda: self.focus("directory"),
            keys.CTRL_J: lambda: self.focus("directory"),
            keys.TAB: lambda: self.focus("preview"),
            "j": lambda: self.selected.renderable.cursor_down(),
            "k": lambda: self.selected.renderable.cursor_up(),
            keys.CTRL_D: lambda: self.selected.renderable.cursor_down(5),
            keys.CTRL_U: lambda: self.selected.renderable.cursor_up(5),
            keys.ENTER: lambda: self.selected.renderable.enter(),
            "c": lambda: self.selected.renderable.open_in_vscode(),
            "v": lambda: self.selected.renderable.open_in_vim(),
            "z": lambda: self.selected.renderable.change_dir(),
            "t": lambda: self.bookmarks.reload(),
        }
        self.selected = self.layout["bookmarks"]
        self.previous = self.layout["preview"]
        self.layout["bookmarks"].renderable.toggle_focus()
        self.bookmarks.enter()
        self.focus("bookmarks")

    def focus(self, element):
        if element == "preview":
            if self.selected is not self.layout["preview"]:
                self.previous = self.selected
                self.selected = self.layout["preview"]
            else:
                self.selected = self.previous
                self.previous = self.layout["preview"]
            self.previous.renderable.toggle_focus()
            self.selected.renderable.toggle_focus()
        else:
            self.selected.renderable.toggle_focus()
            self.selected = self.layout[element]
            self.selected.renderable.toggle_focus()

    def run(self, init=True):
        if init:
            self.setup()
        else:
            self.reload()
        with Live(self.layout, refresh_per_second=60, screen=True):
            result = None
            while result is None:
                try:
                    result = self.bindings[getkey()]()
                except KeyError:
                    pass
                except KeyboardInterrupt:
                    result = self.bindings[keys.CTRL_C]()
        return result

    def stop(self):
        self.console.save_html(
            "/Users/gustavkristensen/prototypes/bookmark/bookmarks/logs.html"
        )
        return 0

    def reload(self):
        self.bookmarks.reload()
