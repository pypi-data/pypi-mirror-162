#!/usr/bin/env python3

from ..error import CardIOError
from ..crypto import crypto_encrypt, crypto_decrypt

class CardCommand:

    def __init__(self, CLA, INS):
        self.CLA = CLA
        self.INS = INS

    def build_request(self):
        raise NotImplementedError("Must override this.")

    def parse_response(self, sw1, sw2, response):
        raise NotImplementedError("Must override this.")

    def __call__(self, connection):
        sw1, sw2, response = self._send_data(connection, self.build_request())
        return self.parse_response(sw1, sw2, response)

    def _send_data(self, connection, data=b""):
        assert type(data) == bytes
        data = list(data)
        # See ISO7816-3. APDU begins with CLA, INS, P1, P2 and ends with
        # an expected count of response bytes. If there's data to send,
        # after the 4-bytes header there's a count of request bytes followed
        # by actual data. Otherwise, both are skipped.
        # In our case, CLA and INS are arguments, P1=P2=0, and always expecting
        # maximum response size(0xFE=254 bytes).
        if data:
            apdu = [self.CLA, self.INS, 0x00, 0x00, len(data)] + data + [0xFE]
        else:
            apdu = [self.CLA, self.INS, 0x00, 0x00, 0xFE]

        response, sw1, sw2 = connection.transmit(apdu)
        response = bytes(response)

        if not ((sw1 == 0x90 and sw2 == 0x00) or sw1 == 0x61):
            if sw1 == 0x88 and sw2 == 0x64:
                response, _, __ = connection.transmit(
                    [0x88, 0x64, 0x00, 0x00, 0xFE])
                response = bytes(response)
            raise CardIOError(sw1=sw1, sw2=sw2, data=response)
        return sw1, sw2, response


class EncryptedCardCommand(CardCommand):

    def __init__(self, CLA, INS):
        CardCommand.__init__(self, CLA, INS)

    def __call__(self, connection, session_key):
        sw1, sw2, response = self._send_data(
            connection,
            crypto_encrypt(session_key, self.build_request())
        )
        return self.parse_response(
            sw1,
            sw2,
            crypto_decrypt(session_key, response)
        )
