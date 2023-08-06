from ._prototype import EncryptedCardCommand

class FC_VAULT_REENCRYPT(EncryptedCardCommand):

    def __init__(self, password):
        assert type(password) == bytes
        EncryptedCardCommand.__init__(self, 0x84, 0x10)
        self.__data = password

    def build_request(self):
        return self.__data 

    def parse_response(self, sw1, sw2, response):
        return response
