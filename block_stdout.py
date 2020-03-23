import sys
import curses
import curses.textpad

class BlockStdout:
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
        self.scr.clear()
        self.scr.addstr(0, 1, f'{self.header}', curses.A_BOLD)
        lines = self.output.split('\n')
        lines = lines[self.scroll:self.scroll+self.nlines]
        for i, line in enumerate(lines, 2):
            self.scr.addstr(i, 1, line)
        curses.textpad.rectangle(self.scr,
                1, 0,
                self.nlines+2,
                min(curses.COLS-1, self.width()-1))

    def width(self):
        return curses.COLS

    def height(self):
        return self.nlines + 3
