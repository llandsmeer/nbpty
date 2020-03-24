import curses
import curses.textpad

import subprocess

from block_base import BlockBase

class BlockEval(BlockBase):
    def __init__(self, header, lines=()):
        self.header = header
        self.output = []
        self.lines = list(lines)
        if not self.lines: self.lines.append('')
        self.scr = curses.newpad(self.height()+1, self.width())
        self.focus = False
        self.cursor = 1 + len(self.lines[-1]), len(self.lines) + 1

    def handle_input(self, key):
        if key == '\n' or key == '\r':
            self.lines.append('')
            self.scr = curses.newpad(self.height()+1, self.width())
        elif key == '\x7f':
            if self.lines[-1]:
                self.lines[-1] = self.lines[-1][:-1]
            elif len(self.lines) > 1:
                del self.lines[-1:]
        elif key == '\x0c':
            self.lines = ['']
        elif key == '\t':
            self.eval()
        else:
            self.lines[-1] += key
        self.cursor = 1 + len(self.lines[-1]), len(self.lines) + 1

    def eval(self):
        try:
            out = subprocess.check_output(['python3', '-c', '\n'.join(self.lines)])
            self.output = out.decode('utf8').rstrip('\n').split('\n')
            self.scr = curses.newpad(self.height()+1, self.width())
        except Exception as ex:
            print(type(ex), ex)

    def render(self):
        super().render()
        for i, line in enumerate(self.lines, 2):
            self.scr.addstr(i, 1, line)
        self.scr.addstr(len(self.lines)+2, 1, '─'*(self.width()-2))
        for i, line in enumerate(self.output, 3+len(self.lines)):
            if line:
                self.scr.addstr(i, 1, line)

    def height(self):
        return len(self.lines) + 3 + 1 + len(self.output)
