#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry
from ..pubsub import publish, subscribe
import struct
import time


class TOTPDisplay(Frame):

    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.number = Label(self, font=("monospace", 20), text="------")
        self.expires = Label(self, text="Press update to get the code.")

        self.number.pack(side="top", expand=False, fill="x")
        self.expires.pack(side="top", expand=False, fill="x")

    def set(self, number):
        if len(number) >= 6:
            number = " ".join([
                number[:len(number) - 6],
                number[-6:-3],
                number[-3:]
            ]).strip()
        self.number.config(text=number)




class TabTOTP(Frame):
    
    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.result = TOTPDisplay(self)
        self.btn_update = Button(self, text="Update")

        self.result.pack(side="top", expand=False, fill="x")
        self.btn_update.pack(side="top", expand=False, fill=None)
        
        self.btn_update.bind("<Button-1>", self.on_do_totp_sha1)

        subscribe("result/totp/sha1", self.on_totp_sha1_result)

        
    def __timecode(self, interval=30):
        num = int(time.time()) // interval 
        bstr = struct.pack('>Q', num)
        return bstr

    def __show_digits(self, digest, digits=6):
        offset = digest[-1] & 0xF
        token_base = digest[offset:offset+4]

        token_val = struct.unpack('>I', token_base)[0] & 0x7fffffff
        token_num = token_val % (10**digits)

        token = str(token_num).rjust(digits, "0")
        return token

    def on_do_totp_sha1(self, *args):
        publish("card/do/vault/totp-sha1", self.__timecode())

    def on_totp_sha1_result(self, code):
        self.result.set(self.__show_digits(code, 8))
