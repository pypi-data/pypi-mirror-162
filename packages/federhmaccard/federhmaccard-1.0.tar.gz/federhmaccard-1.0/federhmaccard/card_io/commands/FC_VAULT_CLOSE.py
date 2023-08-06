from ._prototype import EncryptedCardCommand

class FC_VAULT_CLOSE(EncryptedCardCommand):

    def __init__(self):
        EncryptedCardCommand.__init__(self, 0x84, 0x16)
        self.__data = b""

    def build_request(self):
        return self.__data 

    def parse_response(self, sw1, sw2, response):
        return response
