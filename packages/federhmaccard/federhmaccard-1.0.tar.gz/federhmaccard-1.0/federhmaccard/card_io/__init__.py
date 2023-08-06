#!/usr/bin/env python3

import hashlib
from smartcard.ATR import ATR
from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardMonitoring import CardMonitor
from .crypto import crypto_encrypt, crypto_decrypt
from .observer import FederCardObserver


from .commands._prototype import *
from .commands.FC_GET_CHALLENGE     import * 
from .commands.FC_VERIFY            import * 



"""
declare command &H88 &H88 FACTORY_INIT(LC=0, data as string)
declare command &H88 &H86 FC_FACTORY_RESET(data as string)

declare command &H88 &H00 Greet(LC=0, data as string)

declare command &H88 &H84 FC_GET_CHALLENGE(LC=0, data as string)
declare command &H88 &H20 FC_VERIFY(data as string)


declare command &H84 &H24 FC_CHANGE_PASSWORD(data as string)


declare command &H84 &H00 FC_VAULT_STATUS(LC=0, data as string)
declare command &H84 &H04 FC_VAULT_OPEN(data as string)
declare command &H84 &H08 FC_VAULT_IMPORT(data as string)
declare command &H84 &H10 FC_VAULT_REENCRYPT(data as string)
declare command &H84 &H12 FC_VAULT_HMAC_SHA1(data as string)
declare command &H84 &H14 FC_VAULT_HMAC_SHA256(data as string)
declare command &H84 &H16 FC_VAULT_CLOSE(LC=0, data as string)
"""

from .error import CardIOError
import hmac
import hashlib
from .vault import VaultAccess


def HMAC_SHA256(key, data):
    return hmac.digest(key, data, hashlib.sha256)






class CardSession:

    def __init__(self):
        self.cardRequest = CardRequest(timeout=None) #, cardType=cardtype)
        
        self.cardMonitor = CardMonitor()
        self.cardObserver = FederCardObserver()
        self.cardMonitor.addObserver(self.cardObserver)


    def login(self, password):
        conn = self.cardService.connection
        password = hashlib.sha1(password).digest()
        
        auth_challenge = self.run_command(FC_GET_CHALLENGE())

        session_key = HMAC_SHA256(password, auth_challenge)
        s_res = HMAC_SHA256(password, session_key)
        ret_ok = HMAC_SHA256(session_key, auth_challenge)

        self.__session_key = session_key

        verify_result = self.run_command(FC_VERIFY(s_res))
        verified = (verify_result == ret_ok)

        if not verified:
            self.__session_key = None
        return verified

    def run_command(self, cmd):
        if isinstance(cmd, EncryptedCardCommand):
            return cmd(self.cardService.connection, self.__session_key)
        else:
            return cmd(self.cardService.connection)

    def vault(self, i):
        return VaultAccess(self, i)

    def __enter__(self, *args, **kvargs):
        self.cardService = self.cardRequest.waitforcard()

        self.cardService.connection.connect()
        atr = ATR(self.cardService.connection.getATR())
        identification = bytes(atr.getHistoricalBytes())

        #if identification != b"feder.cards/pg1":
        #    raise Exception("Wrong card inserted.")
        print(identification)

        return self
            

    def __exit__(self, *args, **kvargs):
        self.cardService.connection.disconnect()
        # don't forget to remove observer, or the
        # monitor will poll forever...
        self.cardMonitor.deleteObserver(self.cardObserver)
        self.cardMonitor.stop()
        self.cardObserver = None
