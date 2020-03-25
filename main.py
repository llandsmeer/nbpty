#!/usr/bin/env python3

import sys

import curses
import curses.textpad

from blocks import Blocks
from jupyter_manager import JupyterManager

def main():
    if len(sys.argv) != 2:
        print('usage:', sys.argv[0], '<filename>')
        exit(1)
    filename = sys.argv[1]
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        #stdscr.keypad(True)
        blocks = Blocks(stdscr)
        blocks.add_stdout('Stdout/Stderr', 8)
        manager = JupyterManager(blocks, sys.argv[1])
        manager.launch()
        manager.load(filename)
        stdscr.clear()
        print('Ctrl-J: Move block down')
        print('Ctrl-K: Move block up')
        print('Ctrl-P t: Create terminal')
        print('Ctrl-P e: Run external python')
        print('Ctrl-P o/O: Create new cell')
        print('         -> Press u for history')
        print('         -> Press Tab for eval')
        while True:
            try:
                blocks.render()
                blocks.wait()
                manager.clear_buffers()
                manager.save(filename)
            except KeyboardInterrupt:
                break
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == '__main__':
    main()
