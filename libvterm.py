import ctypes
import faulthandler
faulthandler.enable()

libvterm = ctypes.CDLL('libvterm.so')

def _struct_repr(self):
    fields = ', '.join(f'{key}={getattr(self, key)}' for key, _t in self._fields_)
    return f'{type(self).__name__}({fields})'

class VTermRect(ctypes.Structure):
    _fields_ = [('start_row', ctypes.c_int),
                ('end_row', ctypes.c_int),
                ('start_col', ctypes.c_int),
                ('end_col', ctypes.c_int)]
    __repr__ = _struct_repr

class VTermPos(ctypes.Structure):
    _fields_ = [('row', ctypes.c_int),
                ('col', ctypes.c_int)]
    __repr__ = _struct_repr

class VTermScreenCallbacks(ctypes.Structure):
    _fields_ = [('damage', ctypes.CFUNCTYPE(ctypes.c_int, VTermRect, ctypes.c_void_p)),
                ('moverect', ctypes.CFUNCTYPE(ctypes.c_int, VTermRect, VTermRect, ctypes.c_void_p)),
                ('movecursor', ctypes.CFUNCTYPE(ctypes.c_int, VTermPos, VTermPos, ctypes.c_void_p)),
                ('settermprop', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p)),
                ('bell', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)),
                ('resize', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)),
                ('sb_pushline', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)),
                ('sb_popline', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p))]
    __repr__ = _struct_repr

libvterm.vterm_screen_get_text.argtypes = ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t, VTermRect
libvterm.vterm_obtain_screen.restype = ctypes.c_void_p
libvterm.vterm_new.restype = ctypes.c_void_p

class VTermScreen:
    def __init__(self, width, height):
        self.damage_buf = ctypes.create_string_buffer(8)
        self.chars = [list(' '*width) for _ in range(height)]
        self.term = libvterm.vterm_new(height, width)
        self.callbacks = self.create_callbacks()
        libvterm.vterm_set_utf8(self.term, 1)
        self.screen = libvterm.vterm_obtain_screen(self.term)
        libvterm.vterm_screen_set_callbacks(self.screen, ctypes.pointer(self.callbacks), 0)
        libvterm.vterm_screen_enable_altscreen(self.screen, 1)
        libvterm.vterm_screen_reset(self.screen, 1)
        self.width = width
        self.height = height
        self.cursor = 0, 0

    def create_callbacks(self):
        cb = VTermScreenCallbacks()
        for name, type_ in cb._fields_:
            function = getattr(self, 'vterm_' + name, 0)
            setattr(cb, name, type_(function))
        return cb

    def vterm_damage(self, rect, _user):
        # print('damage', rect)
        for row in range(rect.start_row, rect.end_row):
            for col in range(rect.start_col, rect.end_col):
                try:
                    cell_rect = VTermRect(row, row+1, col, col+1)
                    buf = self.damage_buf
                    n = libvterm.vterm_screen_get_text(self.screen, buf, len(buf), cell_rect)
                    self.chars[row][col] = buf.value[:n].decode('utf8') or ' '
                except:
                    self.chars[row][col] = '?'
        return 1

    def vterm_moverect(self, dst, src, _user):
        return 1

    def vterm_movecursor(self, dst, src, _user):
        self.cursor = dst.col, dst.row
        return 1

    def vterm_settermprop(self, prop, attr, _user):
        # print('settermprop', prop, attr)
        return 1

    def vterm_bell(self, *a):
        print('bell')
        return 1

    def send(self, buf):
        buf = bytearray(buf)
        libvterm.vterm_input_write(self.term, (ctypes.c_char*len(buf)).from_buffer(buf), len(buf))
