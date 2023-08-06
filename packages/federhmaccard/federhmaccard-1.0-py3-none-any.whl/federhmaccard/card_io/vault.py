#!/usr/bin/env python3

from .commands.FC_VAULT_OPEN        import *
from .commands.FC_VAULT_STATUS      import *
from .commands.FC_VAULT_IMPORT      import *
from .commands.FC_VAULT_REENCRYPT   import *
from .commands.FC_VAULT_HMAC_SHA1   import *
from .commands.FC_VAULT_HMAC_SHA256 import *
from .commands.FC_VAULT_CLOSE       import *


class VaultAccess:

    def __init__(self, card_session, vault_id):
        self.session = card_session
        self.vault_id = vault_id

    def __enter__(self, *args, **kvargs):
        return self

    def __exit__(self, *args, **kvargs):
        print(self.close())

    def close(self):
        return self.session.run_command(FC_VAULT_CLOSE())

    @property
    def status(self):
        ret = { 'success': False, 'open': False, 'vault': None }
        st = self.session.run_command(FC_VAULT_STATUS())
        ret['success'] = (st[:3] == b'OK,')
        ret['open'] = st[-1] != 0
        ret['vault'] = None if not ret['open'] else st[-1]
        return ret

    def open(self, password):
        ret = self.session.run_command(FC_VAULT_OPEN(self.vault_id, password))
        print(ret)
        return ret.startswith(b'OK')

    def import_secret(self, secret):
        ret = self.session.run_command(FC_VAULT_IMPORT(self.vault_id, secret))
        print(ret)
        return ret.startswith(b'OK')

    def reencrypt(self, password):
        ret = self.session.run_command(FC_VAULT_REENCRYPT(password))
        print(ret)
        return ret.startswith(b"OK")

    def HMAC_SHA1(self, message):
        ret = self.session.run_command(FC_VAULT_HMAC_SHA1(message))
        if ret.startswith(b'OK,'):
            return ret[3:]
        else:
            print(ret)
            return None

    def HMAC_SHA256(self, message):
        ret = self.session.run_command(FC_VAULT_HMAC_SHA256(message))
        if ret.startswith(b'OK,'):
            return ret[3:]
        else:
            print(ret)
            return None
