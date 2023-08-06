from ._prototype import CardCommand

class FC_VERIFY(CardCommand):

    def __init__(self, verifydata):
        CardCommand.__init__(self, 0x88, 0x20)
        self.__verifydata = verifydata

    def build_request(self):
        return self.__verifydata 

    def parse_response(self, sw1, sw2, response):
        return response
