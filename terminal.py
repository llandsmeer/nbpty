import os
import ctypes
import struct
import fcntl
import select
import termios

from libvterm import VTermScreen

class Terminal:
    def __init__(self, width, height, argv=('/bin/sh',), env=False):
        self.is_alive = True
        self.screen = VTermScreen(width, height)
        self.pid, self.master = os.forkpty()
        if self.pid == 0:
            if env:
                os_env = os.environ.copy()
                os_env.update(env)
                os.execve(argv[0], argv, os_env)
            else:
                os.execv(argv[0], argv)
            exit(4)
        attr = termios.tcgetattr(self.master)
        attr[2] &= ~(termios.ECHO | termios.ECHONL)
        termios.tcsetattr(self.master, termios.TCSAFLUSH, attr)
        self.resize(height, width)

    def resize(self, rows, cols):
        buf = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.master, termios.TIOCSWINSZ, buf)
        self.width = cols
        self.height = rows

    def handle_input(self, event):
        if event == select.POLLIN and self.is_alive:
            buf = os.read(self.master, 1024)
            self.screen.send(buf)
        else:
            self.is_alive = False

    def send(self, buf):
        os.write(self.master, buf.encode('latin1'))
