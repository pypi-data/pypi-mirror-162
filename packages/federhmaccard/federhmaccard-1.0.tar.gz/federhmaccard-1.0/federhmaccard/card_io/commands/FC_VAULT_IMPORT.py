from ._prototype import EncryptedCardCommand

class FC_VAULT_IMPORT(EncryptedCardCommand):

    def __init__(self, vault_id, secret):
        assert type(secret) == bytes
        EncryptedCardCommand.__init__(self, 0x84, 0x08)
        self.__data = bytes([vault_id]) + secret 

    def build_request(self):
        return self.__data 

    def parse_response(self, sw1, sw2, response):
        return response
