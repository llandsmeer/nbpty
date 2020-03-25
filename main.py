#!/usr/bin/env python3

import curses
import curses.textpad

from blocks import Blocks
from jupyter_manager import JupyterManager

def main():
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        #stdscr.keypad(True)
        blocks = Blocks(stdscr)
        blocks.add_stdout('Stdout/Stderr', 8)
        manager = JupyterManager(blocks)
        manager.launch()
        #manager.launch_editor(code='# Press Tab\nprint("hello world\\n"*10)\na = 10')
        #manager.launch_editor(header='Python Cell #2', code='print(a * a)')
        #blocks.add_terminal('Bash', ['/usr/bin/env', 'bash'])
        #blocks.add_terminal('Editor', ['/usr/bin/env', 'vim', '-i', 'NONE', '-u', 'NONE'])
        #blocks.add_terminal('External python console', ['/usr/bin/env', 'python3'])
        blocks.add_text('Scratch')
        stdscr.clear()
        print('Ctrl-J: Move block down')
        print('Ctrl-K: Move block up')
        print('Ctrl-P o/O: Create new cell')
        print('            Press u for history')
        while True:
            try:
                blocks.render()
                blocks.wait()
                manager.clear_buffers()
            except KeyboardInterrupt:
                break
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == '__main__':
    main()
