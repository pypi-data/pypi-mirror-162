from ._prototype import CardCommand

class FC_GET_CHALLENGE(CardCommand):

    def __init__(self):
        CardCommand.__init__(self, 0x88, 0x84)

    def build_request(self):
        return b''

    def parse_response(self, sw1, sw2, response):
        return response
