class CardIOError(IOError):

    def __init__(self, sw1, sw2, data):
        IOError.__init__(self, data)
        self.sw1 = sw1
        self.sw2 = sw2
        self.sw1sw2 = (sw1 << 8) | sw2
        self.data = data
