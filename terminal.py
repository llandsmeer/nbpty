import os
import ctypes
import struct
import fcntl
import termios

libvterm = ctypes.CDLL('libvterm.so')

f = open('log', 'w')

class VTermRect(ctypes.Structure):
    _fields_ = [('start_row', ctypes.c_int),
                ('end_row', ctypes.c_int),
                ('start_col', ctypes.c_int),
                ('end_col', ctypes.c_int)]

class VTermPos(ctypes.Structure):
    _fields_ = [('row', ctypes.c_int),
                ('col', ctypes.c_int)]

class VTermScreenCallbacks(ctypes.Structure):
    _fields_ = [('damage', ctypes.CFUNCTYPE(ctypes.c_int, VTermRect, ctypes.c_void_p)),
                ('moverect', ctypes.CFUNCTYPE(ctypes.c_int, VTermRect, VTermRect, ctypes.c_void_p)),
                ('movecursor', ctypes.CFUNCTYPE(ctypes.c_int, VTermPos, VTermPos, ctypes.c_void_p)),
                ('settermprop', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p)),
                ('bell', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)),
                ('resize', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)),
                ('sb_pushline', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)),
                ('sb_popline', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p))]

class VTermScreen:
    def __init__(self, width, height):
        self.chars = [list(' '*width) for _ in range(height)]
        self.term = libvterm.vterm_new(width, height)
        self.callbacks = self.create_callbacks()
        libvterm.vterm_set_utf8(self.term, 1)
        self.screen = libvterm.vterm_obtain_screen(self.term)
        libvterm.vterm_screen_set_callbacks(self.screen, ctypes.pointer(self.callbacks), 0)
        libvterm.vterm_screen_enable_altscreen(self.screen, 1)
        libvterm.vterm_screen_reset(self.screen, 1)

    def create_callbacks(self):
        cb = VTermScreenCallbacks()
        for name, type_ in cb._fields_:
            function = getattr(self, 'vterm_' + name)
            setattr(cb, name, type_(function))
        return cb

    def vterm_damage(self, rect, _user):
        print('damage', rect, file=f)
        for row in range(rect.start_row, rect.end_row):
            for col in range(rect.start_col, rect.end_col):
                buf = bytearray([0]*10)
                cell_rect = VTermRect(row, col, row+1, col+1)
                libvterm.vterm_screen_get_text(self.screen, buf, len(buf), cell_rect)
                print(buf, file=f)
                self.chars[row][col]
                # CONTINUE HERE

    def vterm_moverect(self, *a):
        print(a, file=f)

    def vterm_movecursor(self, *a):
        print(a, file=f)

    def vterm_settermprop(self, *a):
        print(a, file=f)

    def vterm_bell(self, *a):
        print(a, file=f)

    def vterm_resize(self, *a):
        print(a, file=f)

    def vterm_sb_pushline(self, *a):
        print(a, file=f)

    def vterm_sb_popline(self, *a):
        print(a, file=f)

    def send(self, buf):
        print(buf, file=f)
        buf = bytearray(buf)
        libvterm.vterm_input_write(self.term, (ctypes.c_char*len(buf)).from_buffer(buf), len(buf))

class Terminal:
    def __init__(self, argv=('/bin/bash',)):
        self.screen = VTermScreen(10, 20)
        self.pid, self.master = os.forkpty()
        if self.pid == 0:
            os.execv(argv[0], argv)
            exit(4)
        attr = termios.tcgetattr(self.master)
        attr[2] &= ~(termios.ECHO | termios.ECHONL)
        termios.tcsetattr(self.master, termios.TCSAFLUSH, attr)
        self.output = ''

    def resize(self, rows, cols):
        buf = struct.unpack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.master, termios.TIOCSWINSZ, buf)

    def handle_input(self):
        buf = os.read(self.master, 512)
        self.output = self.output + buf.decode('latin1')
        self.screen.send(buf)

    def send(self, buf):
        os.write(self.master, buf.encode('latin1'))
