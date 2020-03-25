import curses
import curses.textpad

class BlockBase:
    def render(self):
        self.scr.clear()
        self.cursor = None
        self.focus = False
        self.scr.addstr(0, 1, f'{self.header}', curses.A_BOLD)
        curses.textpad.rectangle(self.scr,
                1, 0,
                self.height() - 1,
                min(curses.COLS-1, self.width()-1))

    def is_alive(self):
        return True

    def handle_input(self, key):
        pass

    def width(self):
        return curses.COLS

    def height(self):
        return 3

    def request_exit(self):
        return False
