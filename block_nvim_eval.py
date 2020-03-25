import os
import uuid

import curses
import curses.textpad

import pynvim

import libvterm
from block_base import BlockBase
from terminal import Terminal

class BlockNVimEval(BlockBase):
    def __init__(self, header, width, height, manager, hist=()):
        self._width = width
        self._height = height
        self.header = header
        self.manager = manager
        self.socket_file = os.path.join('/tmp', str(uuid.uuid4()))
        argv = ['/usr/bin/env', 'nvim', '-u', 'NONE']
        env = dict(NVIM_LISTEN_ADDRESS=self.socket_file)
        self.terminal = Terminal(width, height, argv, env=env)
        self.scr = curses.newpad(1, self.width())
        while not os.path.exists(self.socket_file):
            pass
        self.nvim = pynvim.attach('socket', path=self.socket_file)
        self.exec_id = None
        self.output = []
        self.add_hist(hist)

    def add_hist(self, hist):
        orig = list(self.nvim.current.buffer)
        for text in hist:
            self.nvim.current.buffer[:] = text.splitlines()
        self.nvim.current.buffer[:] = orig

    def get_text(self):
        if not self.is_alive():
            return ''
        text = '\n'.join(self.nvim.current.buffer)
        return text

    def set_text(self, text):
        if not self.is_alive():
            return
        self.nvim.current.buffer[:] = text.splitlines()

    def render(self):
        if self.height() > self.scr.getmaxyx()[0] - 1:
            self.scr = curses.newpad(self.height()+1, self.width())
        super().render()
        for y in range(self.terminal.screen.height):
            for x in range(self.terminal.screen.width):
                c = self.terminal.screen.chars[y][x]
                self.scr.addch(y+2, x+1, c)
        self.scr.addstr(self._height+2, 1, '─'*(self.width()-2))
        for i, line in enumerate(self.output, 3+self._height):
            if line:
                self.scr.addstr(i, 1, line)
        x, y = self.terminal.screen.cursor
        self.cursor = x + 1, y + 2

    def is_alive(self):
        return self.terminal.is_alive

    def handle_input(self, key):
        if key == '\t':
            self.eval()
        else:
            self.terminal.send(key)

    def execute_cb(self, out):
        self.output.extend(out.rstrip('\n').split('\n'))
        self.scr = curses.newpad(self.height()+1, self.width())

    def eval(self):
        self.manager.stop_listen(self.exec_id)
        self.output = []
        code = self.get_text()
        self.exec_id = self.manager.execute(code, self.execute_cb)

    def width(self):
        return self._width + 2

    def height(self):
        return self._height + 3 + 1 + len(self.output)

    def request_exit(self):
        self.terminal.close()
