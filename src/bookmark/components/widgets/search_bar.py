from bookmark.components.widgets import BookmarkTree, DirTree
from bookmark.scripts.search import search
import os
from rich.box import ROUNDED
from rich.panel import Panel
from rich.text import Text


class SearchDirTree(DirTree):
    def enter(self):
        layout = self.app.layout["searchbar"]
        for node in self.bar.old_tree.nodes.values():
            node.label = self.bar.old_labels[node.id]
            node.parent = self.bar.old_parents[node.id]
        self.bar.old_tree.cursor = self.bar.searchtree.cursor
        self.bar.searchtree.nodes[self.bar.searchtree.cursor].toggle_highlight()
        self.bar.old_tree.nodes[self.bar.old_tree.cursor].under_cursor = False
        self.bar.old_tree.nodes[self.bar.old_tree.cursor].toggle_highlight()
        self.bar.old_tree.nodes[self.bar.old_tree.cursor].toggle_expand()
        self.bar.old_tree.nodes[self.bar.old_tree.cursor].expand_upward()
        self.bar.old_tree.center()
        layout.visible = False
        self.app.searching.renderable.renderable = self.bar.old_tree
        self.app.mode = None
        self.app.focus("searchbar")
        self.app.focus("searchbar")
        self.bar.clear()


class SearchBar(Panel):
    def __init__(
        self,
        renderable,
        box=ROUNDED,
        *,
        title=None,
        title_align="center",
        subtitle=None,
        subtitle_align="center",
        safe_box=None,
        expand=True,
        style="none",
        border_style="none",
        width=None,
        height=None,
        padding=(0, 1, 0, 1),
        highlight=False,
        app=None,
    ):
        super().__init__(
            renderable,
            box,
            title=title,
            title_align=title_align,
            subtitle=subtitle,
            subtitle_align=subtitle_align,
            safe_box=safe_box,
            expand=expand,
            style=style,
            border_style=border_style,
            width=width,
            height=height,
            padding=padding,
            highlight=highlight,
        )
        self.app = app
        self.text = Text("")
        self.renderable = self.text
        self.focused = False

    def write(self, letter):
        self.text.plain += letter
        self.show_results(self.text.plain)

    def backspace(self):
        self.text.plain = self.text.plain[:-1]
        self.show_results(self.text.plain, backspace=True)

    def strip_labels(self):
        for node in self.nodes.values():
            if isinstance(node.label, Text):
                node.label = node.label.plain
            else:
                node.label = node.label[node.label.rfind("]") + 1 :]

    def clear(self):
        self.text.plain = ""

    def toggle_show(self):
        layout = self.app.layout["searchbar"]
        if layout.visible:
            for node in self.old_tree.nodes.values():
                node.label = self.old_labels[node.id]
                node.parent = self.old_parents[node.id]
            self.searchtree.nodes[self.searchtree.cursor].toggle_highlight()
            self.old_tree.nodes[self.old_tree.cursor].under_cursor = False
            self.old_tree.nodes[self.old_tree.cursor].toggle_highlight()
            self.app.searching.renderable.renderable = self.old_tree
            self.old_tree.center()
            layout.visible = False
        else:
            layout.visible = True
            tree = self.app.searching.renderable.renderable
            tree.nodes[tree.cursor].toggle_highlight()
            if isinstance(tree, BookmarkTree):
                searchtree = BookmarkTree(tree.label, style="cyan", app=self.app)
                searchtree.ignores = tree.ignores
                searchtree.hide_root = True
                searchtree.panel = self.app.layout["bookmarks"].renderable
                searchtree.panel.y_top = 0
            else:
                if tree.label != os.getenv("HOME"):
                    tree.process(recursive=True, max_depth=4)
                searchtree = SearchDirTree(
                    tree.label,
                    style="cyan",
                    guide_style="cyan",
                    app=self.app,
                    ignores=tree.ignores,
                )
                searchtree.panel = self.app.layout["directory"].renderable
                searchtree.panel.y_top = 0
                searchtree.bar = self
            searchtree.children = list(tree.nodes.values())[1:]
            searchtree.nodes = {node.id: node for node in searchtree.children}
            self.old_tree = tree
            self.old_labels = {
                n.id: n.label[n.label.rfind("]") + 1 :] for n in tree.nodes.values()
            }
            self.old_parents = {n.id: n.parent for n in tree.nodes.values()}
            for node in searchtree.nodes.values():
                node.parent = searchtree
            self.app.searching.renderable.renderable = searchtree
            self.nodes = searchtree.nodes
            self.searchtree = searchtree
            try:
                self.searchtree.cursor = self.searchtree.children[0].id
                self.searchtree.nodes[self.searchtree.cursor].under_cursor = False
                self.searchtree.nodes[self.searchtree.cursor].toggle_highlight()
            except IndexError:
                pass
        self.clear()

    def toggle_focus(self):
        if self.focused:
            self.border_style = "blue"
        else:
            self.border_style = "bold green"
        self.focused = not self.focused

    def show_results(self, pattern, backspace=False):
        self.strip_labels()
        self.searchtree.panel.y_top = 0
        if not pattern:
            self.searchtree.children = list(self.nodes.values())
            self.searchtree.nodes = {node.id: node for node in self.searchtree.children}
            try:
                self.nodes[self.searchtree.cursor].toggle_highlight()
                self.searchtree.cursor = self.searchtree.children[0].id
                self.searchtree.nodes[self.searchtree.cursor].under_cursor = False
                self.searchtree.nodes[self.searchtree.cursor].toggle_highlight()
            except IndexError:
                pass
            return
        elif backspace:
            nodes = search(pattern, self.nodes.values())
        else:
            nodes = search(pattern, self.searchtree.nodes.values())
        self.searchtree.children = nodes
        self.searchtree.nodes = {node.id: node for node in self.searchtree.children}
        try:
            self.nodes[self.searchtree.cursor].toggle_highlight()
            self.searchtree.cursor = self.searchtree.children[0].id
            self.searchtree.nodes[self.searchtree.cursor].under_cursor = False
            self.searchtree.nodes[self.searchtree.cursor].toggle_highlight()
        except IndexError:
            pass
