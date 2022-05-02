import os
from bookmark.components.widgets import BookmarkTree, DirTree
from rich.segment import Segment
from rich.syntax import Syntax
from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel, ROUNDED


class ScrollPanel(Panel):
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
        self.focused = False
        self.y_top = 0
        self.app = app

    def toggle_focus(self):
        if self.focused:
            self.border_style = "blue"
        else:
            self.border_style = "bold green"
        self.focused = not self.focused

    def cursor_up(self, lines=1):
        renderable = self.renderable
        if isinstance(renderable, Syntax):
            for _ in range(lines):
                start, end = renderable.line_range
                renderable.line_range = (max(start - 1, 0), end)
        else:
            for _ in range(lines):
                renderable.cursor_up()

    def cursor_down(self, lines=1):
        renderable = self.renderable
        if isinstance(renderable, Syntax):
            for _ in range(lines):
                start, end = renderable.line_range
                renderable.line_range = (start + 1, end)
        else:
            for _ in range(lines):
                renderable.cursor_down()

    def enter(self):
        renderable = self.renderable
        if (
            isinstance(renderable, Syntax)
            or isinstance(renderable, str)
            or isinstance(renderable, Align)
        ):
            pass
        else:
            renderable.enter()

    def open_in_vscode(self):
        renderable = self.renderable
        if isinstance(renderable, Syntax) or isinstance(renderable, Align):
            path = renderable.path
        else:
            path = renderable.cursor_path
        os.system(f"code '{path}'")

    def open_in_vim(self):
        renderable = self.renderable
        if isinstance(renderable, Syntax) or isinstance(renderable, Align):
            path = renderable.path
        else:
            path = renderable.cursor_path
        self.app.mode = None
        self.app.focus("searchbar")
        self.app.toggle_search()
        return f"lvim '{path}'"

    def change_dir(self):
        renderable = self.renderable
        if isinstance(renderable, Syntax) or isinstance(renderable, Align):
            path = renderable.path
        else:
            path = renderable.cursor_path
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        os.chdir(path)
        return "exec /bin/zsh"

    def remove(self):
        renderable = self.renderable
        if isinstance(renderable, BookmarkTree):
            renderable.remove()
        else:
            pass

    def ignore(self):
        renderable = self.renderable
        if isinstance(renderable, DirTree):
            renderable.ignore()
        else:
            pass

    @property
    def actual_height(self):
        return self.app.layout.map[self.layout].region.height

    def __rich_console__(self, console, options):
        _padding = Padding.unpack(self.padding)
        renderable = (
            Padding(self.renderable, _padding) if any(_padding) else self.renderable
        )
        style = console.get_style(self.style)
        border_style = style + console.get_style(self.border_style)
        width = (
            options.max_width
            if self.width is None
            else min(options.max_width, self.width)
        )

        safe_box: bool = console.safe_box if self.safe_box is None else self.safe_box
        box = self.box.substitute(options, safe=safe_box)

        title_text = self._title
        if title_text is not None:
            title_text.style = border_style

        child_width = (
            width - 2
            if self.expand
            else console.measure(
                renderable, options=options.update_width(width - 2)
            ).maximum
        )
        child_height = self.height or options.height or None
        if child_height:
            child_height -= 2
        if title_text is not None:
            child_width = min(
                options.max_width - 2, max(child_width, title_text.cell_len + 2)
            )

        width = child_width + 2
        child_options = options.update(
            width=child_width,
            height=child_height + self.y_top,
            highlight=self.highlight,
        )
        lines = console.render_lines(renderable, child_options, style=style)
        lines = lines[self.y_top : child_height + self.y_top]

        line_start = Segment(box.mid_left, border_style)
        line_end = Segment(f"{box.mid_right}", border_style)
        new_line = Segment.line()
        if title_text is None or width <= 4:
            yield Segment(box.get_top([width - 2]), border_style)
        else:
            title_text.align(self.title_align, width - 4, character=box.top)
            yield Segment(box.top_left + box.top, border_style)
            yield from console.render(title_text, child_options.update_width(width - 4))
            yield Segment(box.top + box.top_right, border_style)

        yield new_line
        for line in lines:
            yield line_start
            yield from line
            yield line_end
            yield new_line

        subtitle_text = self._subtitle
        if subtitle_text is not None:
            subtitle_text.style = border_style

        if subtitle_text is None or width <= 4:
            yield Segment(box.get_bottom([width - 2]), border_style)
        else:
            subtitle_text.align(self.subtitle_align, width - 4, character=box.bottom)
            yield Segment(box.bottom_left + box.bottom, border_style)
            yield from console.render(
                subtitle_text, child_options.update_width(width - 4)
            )
            yield Segment(box.bottom + box.bottom_right, border_style)

        yield new_line
