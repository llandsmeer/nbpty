import sys
import curses
import curses.textpad
import select
from terminal import Terminal
from inputs import Inputs
from libvterm import VTermRect

def handle_stdin():
    buf = sys.stdin.read(512)
    term.send(buf)

def handle_input(ev):
    term.handle_input(ev)

try:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    term = Terminal(curses.COLS-3, curses.LINES-3, ['/usr/bin/env', 'bash']);
    inputs = Inputs()
    inputs.add(0, handle_stdin)
    inputs.add(term.master, handle_input, select.POLLIN | select.POLLHUP)
    while term.is_alive:
        stdscr.clear()
        term.screen.vterm_damage(VTermRect(0, curses.LINES-3, 0, curses.COLS-3), 0)
        for y in range(term.screen.height):
            for x in range(term.screen.width):
                if x >= curses.COLS or y >= curses.LINES:
                    continue
                c = term.screen.chars[y][x]
                stdscr.addch(y+1, x+1, c)
        curses.textpad.rectangle(stdscr, 0, 0, curses.LINES-2, curses.COLS-2)
        stdscr.move(term.screen.cursor[1]+1, term.screen.cursor[0]+1)
        stdscr.refresh()
        inputs.wait()
finally:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
