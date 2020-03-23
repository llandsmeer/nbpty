import os
import ctypes
import struct
import fcntl
import termios

from libvterm import VTermScreen

class Terminal:
    def __init__(self, width, height, argv=('/bin/sh',)):
        self.screen = VTermScreen(width, height)
        self.pid, self.master = os.forkpty()
        if self.pid == 0:
            os.execv(argv[0], argv)
            exit(4)
        attr = termios.tcgetattr(self.master)
        attr[2] &= ~(termios.ECHO | termios.ECHONL)
        termios.tcsetattr(self.master, termios.TCSAFLUSH, attr)
        self.width = width
        self.height = height

    def resize(self, rows, cols):
        buf = struct.unpack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.master, termios.TIOCSWINSZ, buf)
        self.width = cols
        self.height = rows

    def handle_input(self):
        buf = os.read(self.master, 1024)
        self.screen.send(buf)

    def send(self, buf):
        os.write(self.master, buf.encode('latin1'))
