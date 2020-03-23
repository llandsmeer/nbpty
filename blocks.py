import curses
import curses.textpad

from inputs import Inputs
from block_text import BlockText
from block_terminal import BlockTerminal
from block_stdout import BlockStdout

class Blocks:
    def __init__(self, stdscr):
        self.blocks = []
        self.stdscr = stdscr
        self.focus_idx = 0
        self.inputs = Inputs()
        self.inputs.add(0, self.handle_input)

    def handle_input(self):
        try:
            key = self.stdscr.getkey()
        except curses.error as e:
            if str(e) == 'no input':
                return
            raise
        if key == 'J':
            if self.focus_idx < len(self.blocks) - 1:
                self.focus_idx += 1
        elif key == 'K':
            if self.focus_idx > 0:
                self.focus_idx -= 1
        elif self.blocks:
            self.blocks[self.focus_idx].handle_input(key)

    def add_text(self, header, text=''):
        lines = text.split('\n')
        block = BlockText(header, lines)
        self.blocks.append(block)

    def add_terminal(self, header, argv):
        width = curses.COLS - 2
        height = 15
        block = BlockTerminal(header, argv, width, height)
        self.inputs.add(block.terminal.master, block.terminal.handle_input)
        self.blocks.append(block)

    def add_stdout(self, header, nlines):
        block = BlockStdout(header, nlines)
        self.blocks.append(block)

    def render(self):
        top = 0
        focus_top = 0
        for i, block in enumerate(self.blocks):
            block.focus = i == self.focus_idx
            if block.focus:
                focus_top = top
            block.render()
            h = block.height()
            bot = top+h-1
            end = False
            if bot >= curses.LINES:
                bot = curses.LINES - 1
                end = True
            block.scr.refresh(0, 0, top, 0, bot, curses.COLS)
            if end:
                break
            top += h
            if bot >= curses.LINES:
                break
        if self.blocks:
            block = self.blocks[self.focus_idx]
            if True or block.cursor is not None:
                #curses.curs_set(2)
                self.stdscr.move(focus_top + block.cursor[1], block.cursor[0])
                self.stdscr.refresh()
            else:
                #curses.curs_set(0)
                pass


    def wait(self):
        self.inputs.wait()
