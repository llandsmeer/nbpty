import sys

import curses
import curses.textpad
import select

from inputs import Inputs
from block_text import BlockText
from block_terminal import BlockTerminal
from block_stdout import BlockStdout
from block_eval import BlockEval

class Blocks:
    def __init__(self, stdscr):
        self.blocks = []
        self.stdscr = stdscr
        self.focus_idx = 0
        self.inputs = Inputs()
        self.inputs.add(0, self.handle_input)
        self.escape_pressed = False
        self.keybinds = {
            'n': self.action_block_up,
            'p': self.action_block_down,
            'O': self.action_block_create_above,
            'o': self.action_block_create_below
        }

    def handle_block_create_request(self, idx):
        block = BlockText('Created', ['Hi!'])
        self.blocks.insert(self.focus_idx, block)
        self.focus_idx = idx

    def action_block_up(self):
        if self.focus_idx > 0:
            self.focus_idx -= 1

    def action_block_down(self):
        if self.focus_idx < len(self.blocks) - 1:
            self.focus_idx += 1

    def action_block_create_above(self):
        self.handle_block_create_request(self.focus_idx)

    def action_block_create_below(self):
        self.handle_block_create_request(self.focus_idx+1)

    def handle_input(self):
        key = sys.stdin.read(1)
        if not key.isprintable() and not key in '\n\t\x0b\x7f\x0c':
            print(repr(key))
        if self.escape_pressed:
            if key in self.keybinds:
                self.keybinds[key]()
            else:
                print('unknown keybind ^p', repr(key))
            self.escape_pressed = False
        elif key == '\x10': # C-P
            self.escape_pressed = True
        elif key == '\n': # C-J
            self.action_block_down()
        elif key == '\x0b': # C-K
            self.action_block_up()
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
        self.inputs.add(block.terminal.master, block.terminal.handle_input, select.POLLIN | select.POLLHUP)
        self.blocks.append(block)

    def add_stdout(self, header, nlines):
        block = BlockStdout(header, nlines)
        self.blocks.append(block)

    def add_eval(self, header, manager, code=''):
        block = BlockEval(header, manager, code.split('\n'))
        self.blocks.append(block)

    def scroll(self):
        hs = []
        nskip = 0
        for i, block in enumerate(self.blocks):
            h = block.height()
            if i == self.focus_idx:
                top = sum(hs)
                bot = top + h
                while bot > curses.LINES and hs:
                    bot = top + h
                    nskip += 1
                    hs.pop(0)
                    top = sum(hs)
            hs.append(h)
        return nskip

    def render(self):
        for i, block in reversed(list(enumerate(self.blocks))):
            if not block.is_alive():
                self.blocks.pop(i)
        if self.focus_idx >= len(self.blocks):
            self.focus_idx = len(self.blocks) - 1
        focus_top = 0
        top = 0
        nskip = self.scroll()
        self.stdscr.clear()
        self.stdscr.refresh()
        for i, block in enumerate(self.blocks):
            if i < nskip:
                continue
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
            if top >= curses.LINES:
                break
        if self.blocks:
            block = self.blocks[self.focus_idx]
            if block.cursor is not None and 0 <= focus_top + block.cursor[1] < curses.LINES:
                curses.curs_set(2)
                self.stdscr.move(focus_top + block.cursor[1], block.cursor[0])
                self.stdscr.refresh()
            else:
                curses.curs_set(0)

    def wait(self):
        self.inputs.wait()
