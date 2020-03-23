import curses
import curses.textpad

from block_base import BlockBase

class BlockText(BlockBase):
    def __init__(self, header, lines=()):
        self.header = header
        self.lines = list(lines)
        if not lines: lines.append('')
        self.scr = curses.newpad(self.height()+1, self.width())
        self.focus = False
        self.cursor = 1 + len(self.lines[-1]), self.height() - 2

    def handle_input(self, key):
        if key == '\n':
            self.lines.append('')
            self.scr = curses.newpad(self.height()+1, self.width())
        elif key == '\x7f':
            if self.lines[-1]:
                self.lines[-1] = self.lines[-1][:-1]
            elif len(self.lines) > 1:
                del self.lines[-1:]
        elif key == '\x0c':
            self.lines = ['']
        else:
            self.lines[-1] += key
        self.cursor = 1 + len(self.lines[-1]), self.height() - 2

    def render(self):
        super().render()
        for i, line in enumerate(self.lines, 2):
            self.scr.addstr(i, 1, line)

    def height(self):
        return len(self.lines) + 3
