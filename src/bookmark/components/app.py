import os
from getkey import platform, keys
from rich.layout import Layout
from rich.live import Live
from rich.console import Console
from bookmark.components.widgets import ScrollPanel, BookmarkTree, SearchBar


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
                SearchBar("", border_style="blue", app=self),
                name="searchbar",
                size=3,
            ),
            Layout(
                ScrollPanel(
                    "", border_style="blue", title="Directory Overview", app=self
                ),
                name="directory",
            ),
        )
        self.searchbar = layout["searchbar"].renderable
        layout["searchbar"].visible = False
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
            keys.CTRL_X: lambda: self.selected.renderable.remove(),
            keys.ENTER: lambda: self.selected.renderable.enter(),
            "c": lambda: self.selected.renderable.open_in_vscode(),
            "v": lambda: self.selected.renderable.open_in_vim(),
            "z": lambda: self.selected.renderable.change_dir(),
            "r": lambda: self.bookmarks.reload(),
            "\x1d": lambda: self.selected.renderable.ignore(),
        }
        self.selected = self.layout["bookmarks"]
        self.previous_preview = self.layout["preview"]
        self.previous_searchbar = self.layout["searchbar"]
        self.layout["bookmarks"].renderable.toggle_focus()
        self.bookmarks.enter()
        self.focus("bookmarks")

    def focus(self, element):
        if element == "preview":
            if self.selected is not self.layout["preview"]:
                self.previous_preview = self.selected
                self.selected = self.layout["preview"]
            else:
                self.selected = self.previous_preview
                self.previous_preview = self.layout["preview"]
            self.previous_preview.renderable.toggle_focus()
            self.selected.renderable.toggle_focus()
        elif element == "searchbar":
            if self.selected is not self.layout["searchbar"]:
                self.mode = "search"
                self.searching = self.selected
                self.previous_searchbar = self.selected
                self.selected = self.layout["searchbar"]
            else:
                if self.mode == "search_suspended":
                    self.mode = "search"
                    self.previous_searchbar = self.selected
                    self.selected = self.layout["searchbar"]
                elif self.mode == "search":
                    self.mode = None
                    self.selected = self.previous_searchbar
                    self.previous_searchbar = self.layout["searchbar"]
                else:
                    self.mode = "search_suspended"
                    self.selected = self.previous_searchbar
                    self.previous_searchbar = self.layout["searchbar"]
            self.previous_searchbar.renderable.toggle_focus()
            self.selected.renderable.toggle_focus()
        else:
            self.selected.renderable.toggle_focus()
            self.selected = self.layout[element]
            self.selected.renderable.toggle_focus()

    def toggle_search(self):
        if self.mode == "search_suspended":
            self.mode = None
        self.focus("searchbar")
        self.searchbar.toggle_show()

    def run(self, init=True):
        if init:
            self.setup()
        else:
            self.reload()
        with Live(self.layout, refresh_per_second=60, screen=True):
            result = None
            self.mode = None
            while result is None:
                key = getkey()
                if key == "s":
                    if self.mode is None:
                        self.toggle_search()
                    elif self.mode == "search_suspended":
                        self.searchbar.toggle_show()
                        self.toggle_search()
                    elif self.mode == "search":
                        self.searchbar.write(key)
                elif self.mode == "search":
                    if key == keys.ESC:
                        self.toggle_search()
                    elif key == keys.BACKSPACE:
                        self.searchbar.backspace()
                    elif key == keys.ENTER:
                        self.mode = None
                        self.focus("searchbar")
                    elif key.isalnum() or key in ["\\", "/", ".", " "]:
                        self.searchbar.write(key)
                else:
                    if self.mode == "search_suspended":
                        if key == keys.ESC:
                            self.mode = None
                            self.focus("searchbar")
                            self.toggle_search()
                    try:
                        result = self.bindings[key]()
                    except KeyError:
                        pass
                    except KeyboardInterrupt:
                        result = self.bindings[keys.CTRL_C]()
        return result

    def stop(self):
        self.console.save_html(
            "/Users/gustavkristensen/prototypes/bookmark/bookmark/logs.html"
        )
        return 0

    def reload(self):
        self.bookmarks.reload()
