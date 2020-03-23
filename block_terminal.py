import curses
import curses.textpad

from terminal import Terminal

class BlockTerminal:
    def __init__(self, header, argv):
        self.header = header
        self.terminal = Terminal(argv)
        self.focus = False
        self.scr = curses.newpad(1, self.width())

    def render(self):
        if self.height() > self.scr.getmaxyx()[0] - 1:
            self.scr = curses.newpad(self.height()+1, self.width())
        self.scr.clear()
        self.scr.addstr(0, 1, f'{self.header}', curses.A_BOLD)
        for i, line in enumerate(self.terminal.output.split('\n'), 2):
            self.scr.addstr(i, 1, line)
        if self.focus:
            curses.textpad.rectangle(self.scr,
                    1, 0,
                    self.height() - 1,
                    min(curses.COLS-1, self.width()-1))

    def handle_input(self, key):
        self.terminal.send(key)

    def width(self):
        return curses.COLS

    def height(self):
        return len(self.terminal.output.split('\n')) + 1 + 2
