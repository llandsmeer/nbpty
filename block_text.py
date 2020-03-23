import curses
import curses.textpad

class BlockText:
    def __init__(self, header, lines):
        self.header = header
        self.lines = list(lines)
        self.scr = curses.newpad(self.height()+1, self.width())
        self.focus = False
        self.cursor = 0, 2

    def handle_input(self, key):
        self.lines[2] += key
        self.cursor = 0, len(self.lines[2])

    def render(self):
        self.scr.clear()
        self.scr.addstr(0, 1, f'{self.header}', curses.A_BOLD)
        for i, line in enumerate(self.lines, 2):
            self.scr.addstr(i, 1, line)
        if self.focus:
            curses.textpad.rectangle(self.scr,
                    1, 0,
                    len(self.lines)+2,
                    min(curses.COLS-1, self.width()-1))

    def width(self):
        return curses.COLS

    def height(self):
        return len(self.lines) + 3
