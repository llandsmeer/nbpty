import curses
import curses.textpad

from blocks import Blocks

def main():
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        #stdscr.keypad(True)
        blocks = Blocks(stdscr)
        blocks.add_text('Title', 'content\nhello world\n')
        blocks.add_terminal('vim', ['/usr/bin/env', 'vim', '-i', 'NONE', '-u', 'NONE'])
        blocks.add_terminal('Bash', ['/usr/bin/env', 'bash'])
        blocks.add_terminal('Python', ['/usr/bin/env', 'python3'])
        stdscr.clear()
        while True:
            try:
                blocks.render()
                blocks.wait()
            except KeyboardInterrupt:
                break
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == '__main__':
    main()
