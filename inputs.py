import os
import fcntl
import select

class Inputs:
    def __init__(self):
        self.poll = select.poll()
        self.map = {}

    def add(self, fd, f, mask=select.POLLIN):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self.poll.register(fd, mask)
        self.map[fd] = f

    def wait(self):
        for fd, event in self.poll.poll():
            self.map[fd]()
