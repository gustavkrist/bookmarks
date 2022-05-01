import json
import os
from bookmark.components.widgets import ControlTree
from bookmark.scripts import del_bookmark, ignore_element
from bisect import bisect
from rich.syntax import Syntax
from rich.align import Align
from rich.panel import Panel


class BookmarkNode(ControlTree):
    def __init__(
        self,
        label,
        *,
        style="tree",
        guide_style="tree.line",
        expanded=True,
        highlight=False,
        hide_root=False,
        app=None,
        parent=None,
        tree=None,
        type="dir",
        id=0,
        path="",
    ):
        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
            hide_root=hide_root,
            app=app,
            parent=parent,
        )
        self.tree = tree
        self.type = type
        self.id = id
        self.path = path

    def add(
        self,
        label,
        *,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
        app=None,
        tree=None,
        type="dir",
        path="",
    ):
        node = BookmarkNode(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            highlight=self.highlight if highlight is None else highlight,
            app=self.app if app is None else app,
            tree=self.tree if tree is None else tree,
            type=type,
            parent=self,
            id=self.tree.max_id,
            path=path,
        )
        self.tree.max_id += 1
        self.tree.nodes[node.id] = node
        self.children.append(node)
        return node

    def toggle_expand(self):
        self.expanded = not self.expanded

    def preview(self):
        try:
            syntax = Syntax.from_path(
                self.path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="ansi_dark",
                line_range=(0, None),
            )
        except Exception:
            syntax = Align(
                Panel(
                    "Cannot render binary file",
                    expand=False,
                    height=3,
                    border_style="red",
                    style="bold",
                ),
                align="center",
                vertical="middle",
            )
            os.system(f"open '{self.path}'")
        syntax.path = self.path
        self.app.layout["preview"].renderable.renderable = syntax
        self.app.layout[
            "preview"
        ].renderable.title = f"Preview - {os.path.basename(self.path)}"


class DirNode(BookmarkNode):
    def __init__(
        self,
        label,
        *,
        style="tree",
        guide_style="tree.line",
        expanded=True,
        highlight=False,
        hide_root=False,
        app=None,
        parent=None,
        tree=None,
        type="dir",
        id=0,
        path="",
        ignores=[],
    ):
        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
            hide_root=hide_root,
            app=app,
            parent=parent,
        )
        self.tree = tree
        self.type = type
        self.id = id
        self.path = path
        self.processed = not bool(type == "dir")
        self.permission_denied = False
        self.ignores = ignores

    def add(
        self,
        label,
        *,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
        app=None,
        tree=None,
        type="dir",
        path="",
        ignores=[],
    ):
        node = DirNode(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            highlight=self.highlight if highlight is None else highlight,
            app=self.app if app is None else app,
            tree=self.tree if tree is None else tree,
            type=type,
            parent=self,
            id=self.tree.max_id,
            path=path,
            ignores=self.ignores if not ignores else ignores,
        )
        self.tree.max_id += 1
        self.tree.nodes[node.id] = node
        self.children.append(node)
        return node

    def add_recursive(self, path, depth=0, max_depth=-1):
        if max_depth >= 0 and depth > max_depth:
            return
        try:
            dir_tree = [el for el in os.listdir(path) if el not in self.ignores]
        except PermissionError:
            self.style = "red"
            self.permission_denied = True
            return
        dirs = [dir for dir in dir_tree if os.path.isdir(f"{path}/{dir}")]
        files = [file for file in dir_tree if file not in dirs]
        for dir in sorted(dirs):
            child = self.add(
                dir, style="magenta", type="dir", expanded=False, path=f"{path}/{dir}"
            )
            child.add_recursive(f"{path}/{dir}", depth + 1, max_depth)
            child.expanded = False
        for file in sorted(files):
            child = self.add(file, style="cyan", type="file", path=f"{path}/{file}")

    def process(self, depth=0, recursive=False, max_depth=-1):
        if max_depth >= 0 and depth > max_depth:
            return
        elif self.processed and not recursive:
            return
        elif self.type == "file":
            return
        path = self.path
        try:
            dir_tree = [el for el in os.listdir(path) if el not in self.ignores]
        except PermissionError:
            self.style = "red"
            self.permission_denied = True
            return
        dirs = [dir for dir in dir_tree if os.path.isdir(f"{path}/{dir}")]
        files = [file for file in dir_tree if file not in dirs]
        for dir in sorted(dirs):
            child = self.add(
                dir, style="magenta", type="dir", expanded=False, path=f"{path}/{dir}"
            )
            child.expanded = False
        for file in sorted(files):
            child = self.add(file, style="cyan", type="file", path=f"{path}/{file}")
        if recursive:
            for child in self.children:
                child.process(depth=depth + 1, recursive=recursive)

    def toggle_expand(self):
        if self.permission_denied:
            return
        try:
            if not self.children[0].processed:
                for child in self.children:
                    if not child.processed:
                        child.process()
        except IndexError:
            pass
        self.expanded = not self.expanded

    def reload(self):
        if not self.children:
            return
        children_dict = {c.label[c.label.rfind("]") + 1 :]: c for c in self.children}
        elements = [el for el in os.listdir(self.path) if el not in self.ignores]
        removed_nodes = [label for label in children_dict if label not in elements]
        added_nodes = [element for element in elements if element not in children_dict]
        if removed_nodes:
            for label in removed_nodes:
                node = children_dict[label]
                self.children.remove(node)
                stack = [node]
                while stack:
                    removed = stack.pop()
                    for child in removed.children:
                        stack.append(child)
                    self.tree.nodes.pop(removed.id)
        if added_nodes:
            dir_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "dir"
            ]
            file_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "file"
            ]
            split = len(dir_nodes)
            for label in added_nodes:
                path = f"{self.path}/{label}"
                type = "dir" if os.path.isdir(path) else "file"
                style = "magenta" if type == "dir" else "cyan"
                self.add(label, style=style, type=type, expanded=False, path=path)
                child = self.children.pop()
                child.expanded = False
                if type == "dir":
                    insertion_point = bisect(dir_nodes, label)
                else:
                    insertion_point = bisect(file_nodes, label) + split
                self.children.insert(insertion_point, child)
                self.tree.nodes[child.id] = child
                child.expanded = False
                child.process()
        for child in self.children:
            child.ignores = self.ignores
            child.reload()

    def expand_upward(self):
        node = self
        while node != node.tree:
            if not node.expanded:
                node.expanded = True
            node = node.parent


class DirTree(ControlTree):
    def __init__(
        self,
        label,
        *,
        style="tree",
        guide_style="tree.line",
        expanded=True,
        highlight=False,
        hide_root=False,
        app=None,
        parent=None,
        ignores=[],
    ):
        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
            hide_root=hide_root,
            app=app,
            parent=parent,
        )
        self.tree = self
        self.type = type
        self.id = 0
        self.max_id = 1
        self.nodes = {0: self}
        self.type = "dir"
        self.cursor = 0
        self.path = label
        self.ignores = ignores

    def add(
        self,
        label,
        *,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
        app=None,
        tree=None,
        type="dir",
        path="",
        ignores=[],
    ):
        node = DirNode(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            highlight=self.highlight if highlight is None else highlight,
            app=self.app if app is None else app,
            tree=self.tree if tree is None else tree,
            type=type,
            parent=self,
            id=self.max_id,
            path=path,
            ignores=self.ignores if not ignores else ignores,
        )
        self.max_id += 1
        self.nodes[node.id] = node
        self.children.append(node)
        return node

    def initialize(self, path):
        self.tree = self
        self.id = 0
        self.max_id = 1
        self.nodes = {0: self}
        self.add_recursive(path)
        self.cursor = self.children[0].id
        cursor_node = self.nodes[self.cursor]
        cursor_node.toggle_highlight()

    def add_recursive(self, path, max_depth=1):
        self._add_recursive(path, max_depth=max_depth)
        self.cursor = self.children[0].id
        cursor_node = self.nodes[self.cursor]
        cursor_node.toggle_highlight()

    def _add_recursive(self, path, depth=0, max_depth=-1):
        if max_depth >= 0 and depth > max_depth:
            return
        try:
            dir_tree = [el for el in os.listdir(path) if el not in self.ignores]
        except PermissionError:
            self.style = "red"
            self.permission_denied = True
            return
        dirs = [dir for dir in dir_tree if os.path.isdir(f"{path}/{dir}")]
        files = [file for file in dir_tree if file not in dirs]
        for dir in sorted(dirs):
            child = self.add(
                dir, style="magenta", type="dir", expanded=False, path=f"{path}/{dir}"
            )
            child.add_recursive(f"{path}/{dir}", depth + 1, max_depth)
            child.expanded = False
        for file in sorted(files):
            child = self.add(file, style="cyan", type="file", path=f"{path}/{file}")

    def enter(self):
        node = self.nodes[self.cursor]
        if node.type == "dir":
            node.toggle_expand()
        else:
            node.preview()

    def toggle_expand(self):
        self.expanded = not self.expanded

    def reload(self):
        if not self.children:
            return
        children_dict = {c.label[c.label.rfind("]") + 1 :]: c for c in self.children}
        elements = [el for el in os.listdir(self.path) if el not in self.ignores]
        removed_nodes = [label for label in children_dict if label not in elements]
        added_nodes = [element for element in elements if element not in children_dict]
        if removed_nodes:
            for label in removed_nodes:
                node = children_dict[label]
                self.children.remove(node)
                stack = [node]
                while stack:
                    removed = stack.pop()
                    for child in removed.children:
                        stack.append(child)
                    self.tree.nodes.pop(removed.id)
        if added_nodes:
            dir_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "dir"
            ]
            file_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "file"
            ]
            split = len(dir_nodes)
            for label in added_nodes:
                path = f"{self.path}/{label}"
                type = "dir" if os.path.isdir(path) else "file"
                style = "magenta" if type == "dir" else "cyan"
                self.add(label, style=style, type=type, expanded=False, path=path)
                child = self.children.pop()
                child.expanded = False
                if type == "dir":
                    insertion_point = bisect(dir_nodes, label)
                else:
                    insertion_point = bisect(file_nodes, label) + split
                self.children.insert(insertion_point, child)
                self.tree.nodes[child.id] = child
                child.expanded = False
                child.process()
        for child in self.children:
            child.ignores = self.ignores
            child.reload()
        if self.cursor not in self.nodes:
            self.cursor = 0
            self.nodes[self.cursor].toggle_highlight()
            self.center()

    def process(self, recursive=False, max_depth=-1):
        for child in self.children:
            child.process(recursive=recursive, max_depth=max_depth)

    def ignore(self):
        label = self.bookmark_name
        try:
            element = self.nodes[self.cursor].label.plain
        except AttributeError:
            node = self.nodes[self.cursor]
            element = node.label[node.label.rfind("]") + 1 :]
        ignore_element(label, element)
        self.ignores.append(element)
        self.reload()


class BookmarkTree(ControlTree):
    def __init__(
        self,
        label,
        *,
        style="tree",
        guide_style="tree.line",
        expanded=True,
        highlight=False,
        hide_root=True,
        app=None,
        parent=None,
    ):
        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
            hide_root=hide_root,
            app=app,
            parent=parent,
        )
        self.tree = self
        self.id = 0
        self.max_id = 1
        self.nodes = {0: self}
        self.dir_trees = {}
        self.cursor = 0

    def add(
        self,
        label,
        *,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
        app=None,
        tree=None,
        type="dir",
        path="",
    ):
        node = BookmarkNode(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            highlight=self.highlight if highlight is None else highlight,
            app=self.app if app is None else app,
            tree=self.tree if tree is None else tree,
            type=type,
            parent=self,
            id=self.max_id,
            path=path,
        )
        self.max_id += 1
        self.nodes[node.id] = node
        self.children.append(node)
        return node

    def load_file(self, file_path):
        with open(file_path, "r") as f:
            json_dict = json.load(f)
            bookmarks = json_dict["bookmarks"]
            ignores = json_dict["ignores"]
            dir_bookmarks = []
            file_bookmarks = []
            for label, path in bookmarks.items():
                if os.path.isdir(path):
                    dir_bookmarks.append((label, path))
                else:
                    file_bookmarks.append((label, path))
            for label, path in sorted(dir_bookmarks):
                self.add(label, style="magenta", path=path, type="dir")
            for label, path in sorted(file_bookmarks):
                self.add(label, path=path, type="file")
        self.ignores = ignores
        self.cursor = self.children[0].id
        cursor_node = self.nodes[self.cursor]
        cursor_node.toggle_highlight()

    def cursor_up(self):
        cursor_node = self.nodes[self.cursor]
        previous_node = cursor_node.previous_node
        if previous_node is not None and previous_node is not self.tree:
            cursor_node.toggle_highlight()
            previous_node.toggle_highlight()
            self.cursor = previous_node.id

    def enter(self):
        node = self.nodes[self.cursor]
        if node.type == "dir":
            self.show_tree(node)
        else:
            node.preview()

    def show_tree(self, node):
        dir_tree = self.dir_trees.get(node.id, None)
        ignores = []
        try:
            node.label = node.label.plain
        except AttributeError:
            pass
        try:
            ignores += self.ignores["global"]
        except KeyError:
            pass
        try:
            ignores += self.ignores[node.label[node.label.rfind("]") + 1 :]]
        except KeyError:
            pass
        if dir_tree is None:
            dir_tree = DirTree(
                node.path,
                style="cyan",
                guide_style="cyan",
                app=self.app,
                ignores=ignores,
            )
            dir_tree.add_recursive(node.path)
            dir_tree.panel = self.app.layout["directory"].renderable
            dir_tree.panel.y_top = 0
            dir_tree.bookmark_name = node.label[node.label.rfind("]") + 1 :]
            self.dir_trees[node.id] = dir_tree
        else:
            dir_tree.ignores = ignores
            dir_tree.reload()
            dir_tree.center()
        self.app.layout["directory"].renderable.renderable = dir_tree
        self.app.focus("directory")

    def reload(self):
        if os.getenv("BOOKMARK_PATH") is not None:
            path = f"{os.getenv('BOOKMARK_PATH')}"
        else:
            path = f"{os.getenv('HOME')}/.bookmarks"
        with open(path, "r") as f:
            json_dict = json.load(f)
            bookmarks = json_dict["bookmarks"]
            ignores = json_dict["ignores"]
        children_dict = {c.label[c.label.rfind("]") + 1 :]: c for c in self.children}
        removed_nodes = [label for label in children_dict if label not in bookmarks]
        added_nodes = [element for element in bookmarks if element not in children_dict]
        for label in removed_nodes:
            node = children_dict[label]
            self.children.remove(node)
            self.nodes.pop(node.id)
        if added_nodes:
            dir_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "dir"
            ]
            file_nodes = [
                c.label[c.label.rfind("]") + 1 :]
                for c in self.children
                if c.type == "file"
            ]
            split = len(dir_nodes)
            for label in added_nodes:
                path = bookmarks[label]
                type = "dir" if os.path.isdir(path) else "file"
                style = "magenta" if type == "dir" else "cyan"
                self.add(label, style=style, type=type, path=path)
                child = self.children.pop()
                if type == "dir":
                    insertion_point = bisect(dir_nodes, label)
                else:
                    insertion_point = bisect(file_nodes, label) + split
                self.children.insert(insertion_point, child)
                self.tree.nodes[child.id] = child
        self.ignores = ignores
        selected = self.app.selected
        for id, tree in list(self.dir_trees.items()):
            if id not in self.nodes:
                self.dir_trees.pop(id)
        if self.cursor not in self.nodes:
            self.cursor = self.children[0].id
            self.nodes[self.cursor].toggle_highlight()
            self.show_tree(self.nodes[self.cursor])
        else:
            node = self.nodes[self.cursor]
            ignores = []
            try:
                ignores += self.ignores["global"]
            except KeyError:
                pass
            try:
                ignores += self.ignores[node.label[node.label.rfind("]") + 1 :]]
            except KeyError:
                pass
            self.app.layout["directory"].renderable.renderable.ignores = ignores
        self.app.layout["directory"].renderable.renderable.reload()
        self.app.focus(selected.name)

    def remove(self):
        node = self.nodes[self.cursor]
        label = node.label[node.label.rfind("]") + 1 :]
        del_bookmark(label)
        self.reload()
