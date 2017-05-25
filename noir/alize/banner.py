import os

class Banner(object):
    def __init__(self):
        self.version = 0
        self.length = 0
        self.pid = 0
        self.real_width = 0
        self.real_height = 0
        self.virtual_width = 0
        self.virtual_height = 0
        self.orientation = 0
        self.quirks = 0

    def toString(self):
        return "Banner [Version=" + str(self.version) + \
               ", length=" + str(self.length) + \
               ", Pid=" + str(self.pid) + \
               ", realWidth=" +  str(self.real_width) + \
               ", realHeight=" +  str(self.real_height) + \
               ", virtualWidth=" +  str(self.virtual_width) + \
               ", virtualHeight=" +  str(self.virtual_height) + \
               ", orientation=" +  str(self.orientation) +", quirks=" +  str(self.quirks) + "]"
