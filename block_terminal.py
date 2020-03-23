import curses
import curses.textpad

from block_base import BlockBase
from terminal import Terminal
import libvterm

class BlockTerminal(BlockBase):
    def __init__(self, header, argv, width, height):
        self._width = width
        self._height = height
        self.header = header
        self.terminal = Terminal(width, height, argv)
        self.focus = False
        self.scr = curses.newpad(1, self.width())
        self.cursor = None

    def render(self):
        if self.height() > self.scr.getmaxyx()[0] - 1:
            self.scr = curses.newpad(self.height()+1, self.width())
        super().render()
        for y in range(self.terminal.screen.height):
            for x in range(self.terminal.screen.width):
                c = self.terminal.screen.chars[y][x]
                self.scr.addch(y+2, x+1, c)
        x, y = self.terminal.screen.cursor
        self.cursor = x + 1, y + 2

    def is_alive(self):
        return self.terminal.is_alive

    def handle_input(self, key):
        self.terminal.send(key)

    def width(self):
        return self._width + 2

    def height(self):
        return self._height + 3
