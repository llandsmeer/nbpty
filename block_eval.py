import curses
import curses.textpad

from block_base import BlockBase

class BlockEval(BlockBase):
    def __init__(self, header, manager, lines=()):
        self.header = header
        self.output = []
        self.lines = list(lines)
        if not self.lines: self.lines.append('')
        self.scr = curses.newpad(self.height()+1, self.width())
        self.focus = False
        self.cursor = 1 + len(self.lines[-1]), len(self.lines) + 1
        self.manager = manager
        self.exec_id = None

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
        elif key == 'O':
            self.manager.history(print)
        else:
            self.lines[-1] += key
        self.cursor = 1 + len(self.lines[-1]), len(self.lines) + 1

    def execute_cb(self, out):
        self.output.extend(out.rstrip('\n').split('\n'))
        self.scr = curses.newpad(self.height()+1, self.width())

    def eval(self):
        self.manager.stop_listen(self.exec_id)
        self.output = []
        code = '\n'.join(self.lines)
        self.exec_id = self.manager.execute(code, self.execute_cb)

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
