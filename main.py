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
        blocks.add_stdout('Stdout/Stderr', 8)
        blocks.add_terminal('Bash', ['/usr/bin/env', 'bash'])
        blocks.add_text('Scratch')
        blocks.add_eval('Python Cell', '# Press Tab\nprint("hello world\\n"*10)')
        blocks.add_terminal('Editor', ['/usr/bin/env', 'vim', '-i', 'NONE', '-u', 'NONE'])
        blocks.add_terminal('Python console', ['/usr/bin/env', 'python3'])
        blocks.add_text('Scratch')
        blocks.add_text('Scratch')
        stdscr.clear()
        print('Ctrl-J: Move block down')
        print('Ctrl-K: Move block up')
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
