from ._prototype import EncryptedCardCommand

class FC_VAULT_STATUS(EncryptedCardCommand):

    def __init__(self):
        EncryptedCardCommand.__init__(self, 0x84, 0x00)
        self.__data = b""

    def build_request(self):
        return self.__data 

    def parse_response(self, sw1, sw2, response):
        return response
