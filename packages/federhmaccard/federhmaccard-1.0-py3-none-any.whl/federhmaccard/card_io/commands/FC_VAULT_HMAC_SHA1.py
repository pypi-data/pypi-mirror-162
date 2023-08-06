from ._prototype import EncryptedCardCommand

class FC_VAULT_HMAC_SHA1(EncryptedCardCommand):

    def __init__(self, message):
        assert type(message) == bytes
        EncryptedCardCommand.__init__(self, 0x84, 0x12)
        self.__data = message 

    def build_request(self):
        return self.__data 

    def parse_response(self, sw1, sw2, response):
        return response
