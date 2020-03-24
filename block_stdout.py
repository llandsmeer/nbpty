import sys
import curses
import curses.textpad
import textwrap

from block_base import BlockBase

class BlockStdout(BlockBase):
    def __init__(self, header, nlines):
        self.header = header
        self.nlines = nlines
        self.scr = curses.newpad(self.height()+1, self.width())
        self.focus = False
        self.cursor = 1, 2
        self.orig = sys.stderr
        sys.stdout = self
        sys.stderr = self
        self.output = ''
        self.scroll = 0
        self.f = open('log', 'w')

    def lines(self):
        lines = []
        for line in self.output.split('\n'):
            lines.extend(textwrap.wrap(line, self.width()-2))
        return lines

    def handle_input(self, key):
        if key == 'j':
            self.scroll += 1
        if key == 'k':
            self.scroll -= 1
        if self.scroll < 0:
            self.scroll = 0
        n = self.output.count('\n') + 1
        if self.scroll > n - 2:
            self.scroll = n - 2

    def write(self, s):
        #self.orig.write(s)
        self.f.write(s)
        self.f.flush()
        self.output = self.output + str(s)
        n = self.output.count('\n') + 1
        if n > self.nlines:
            self.scroll = n - self.nlines
        else:
            self.scroll = 0

    def flush(self):
        pass

    def render(self):
        super().render()
        lines = self.lines()
        lines = lines[self.scroll:self.scroll+self.nlines]
        for i, line in enumerate(lines, 2):
            self.scr.addstr(i, 1, line)

    def height(self):
        return self.nlines + 3
