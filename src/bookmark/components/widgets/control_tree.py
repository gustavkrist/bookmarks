from rich.tree import Tree


class ControlTree(Tree):
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
    ):
        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
            hide_root=hide_root,
        )
        self.under_cursor = False
        self.parent = parent
        self.app = app

    def add(
        self,
        label,
        *,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
    ):
        node = ControlTree(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            highlight=self.highlight if highlight is None else highlight,
            parent=self,
        )
        self.children.append(node)
        return node

    def toggle_highlight(self):
        if self.under_cursor:
            try:
                self.label = self.label[self.label.rfind("]") + 1 :]
            except AttributeError:
                self.label.style = "none"
        else:
            try:
                self.label = "[bold italic]" + self.label
            except TypeError:
                self.label.style = "bold italic"
                pass
        self.under_cursor = not self.under_cursor

    def cursor_down(self):
        cursor_node = self.nodes[self.cursor]
        next_node = cursor_node.next_node
        if next_node is not None:
            cursor_node.toggle_highlight()
            next_node.toggle_highlight()
            self.cursor = next_node.id
        cursor_line = self.cursor_line
        tree_height = self.visible_height
        panel_height = self.panel.actual_height
        y_top = self.panel.y_top
        if (
            panel_height // 2 - 3 < cursor_line - y_top
            and tree_height - y_top + 2 > panel_height
        ):
            self.panel.y_top += 1

    def cursor_up(self):
        cursor_node = self.nodes[self.cursor]
        previous_node = cursor_node.previous_node
        if previous_node is not None:
            cursor_node.toggle_highlight()
            previous_node.toggle_highlight()
            self.cursor = previous_node.id
        cursor_line = self.cursor_line
        panel_height = self.panel.actual_height
        y_top = self.panel.y_top
        if cursor_line - y_top < panel_height // 2 and y_top > 0:
            self.panel.y_top -= 1

    def center(self):
        cursor_line = self.cursor_line
        tree_height = self.visible_height
        panel_height = self.panel.actual_height
        if tree_height <= panel_height or cursor_line < panel_height:
            y_top = 0
            while (
                panel_height // 2 - 3 < cursor_line - y_top
                and tree_height - y_top + 2 > panel_height
            ):
                y_top += 1
        elif tree_height - cursor_line <= panel_height:
            y_top = tree_height - panel_height + 2
        else:
            y_top = cursor_line + 3 - panel_height // 2
        self.panel.y_top = y_top

    @property
    def next_node(self):
        if self.expanded and self.children:
            return self.children[0]
        else:
            sibling = self.next_sibling
            if sibling is not None:
                return sibling

            node = self
            while True:
                if node.parent is None:
                    return None
                sibling = node.parent.next_sibling
                if sibling is not None:
                    return sibling
                else:
                    node = node.parent

    @property
    def previous_node(self):
        sibling = self.previous_sibling
        if sibling is not None:

            def last_sibling(node):
                if node.expanded and node.children:
                    return last_sibling(node.children[-1])
                else:
                    return (
                        node.children[-1] if node.children and node.expanded else node
                    )

            return last_sibling(sibling)

        if self.parent is None:
            return None
        return self.parent

    @property
    def next_sibling(self):
        if self.parent is None:
            return None
        iter_siblings = iter(self.parent.children)
        try:
            for node in iter_siblings:
                if node is self:
                    return next(iter_siblings)
        except StopIteration:
            pass
        return None

    @property
    def previous_sibling(self):
        if self.parent is None:
            return None
        iter_siblings = iter(self.parent.children)
        sibling = None

        for node in iter_siblings:
            if node is self:
                return sibling
            sibling = node
        return None

    @property
    def cursor_line(self):
        line = 0
        node = self
        while node.id != self.cursor:
            node = node.next_node
            line += 1
        return line

    @property
    def visible_height(self):
        height = 0
        node = self
        while node is not None:
            node = node.next_node
            height += 1
        return height

    @property
    def cursor_path(self):
        return self.nodes[self.cursor].path
