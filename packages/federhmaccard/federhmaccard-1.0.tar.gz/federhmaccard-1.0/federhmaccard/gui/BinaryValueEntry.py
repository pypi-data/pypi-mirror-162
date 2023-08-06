#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry
import re
import base64

ENCODINGS = ["Plain", "HEX", "Base32", "Base64"]

class BinaryValueEntry(Frame):

    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.entry = ValueEntry(self)
        self.encoding = ttk.Combobox(
            self,
            state="readonly",
            values=ENCODINGS
        )
        self.encoding.current(0)

        self.hexvalue = StringVar()

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.entry.grid(row=0, column=0, sticky="news")
        self.encoding.grid(row=0, column=1, sticky="news")

        self.entry.value.trace_add("write", self.on_value_changed)
#        self.entry.bind("<KeyPress>", self.on_value_changed)
#        self.entry.bind("<FocusOut>", self.on_value_changed)
        self.encoding.bind("<<ComboboxSelected>>", self.on_value_changed)

        self.onchanged = None

    def clear(self):
        self.entry.value.set("")

    def set_bytes_to_hex_value(self, b):
        self.entry.value.set(b.hex())
        self.encoding.current(ENCODINGS.index("HEX"))
        self.on_value_changed()

    def on_value_changed(self, *args):
        inputvalue = self.entry.value.get()
        encoding = ENCODINGS[self.encoding.current()].lower()
        error = False
        outputvalue = ""

        if inputvalue == "":
            outputvalue = b""
            error = False
        else:
            if not re.match("^[\x20-\x7e]+$", inputvalue):
                error = True
            else:
                try:
                    if encoding == "plain":
                        outputvalue = inputvalue.encode("ascii")
                    elif encoding == "base32":
                        inputvalue += ("=" * ((8 - (len(inputvalue) % 8)) % 8))
                        outputvalue = base64.b32decode(inputvalue, casefold=True)
                    elif encoding == "base64":
                        outputvalue = base64.b64decode(inputvalue)
                    elif encoding == "hex":
                        outputvalue = bytes.fromhex(inputvalue)
                except Exception as e:
                    print("Error decoding user input:", e)
                    error = True
        def setnewvalue(v):
            if self.hexvalue.get() != v:
                self.hexvalue.set(v)

        if not error:
            self.entry.config(bg="white")
            setnewvalue(outputvalue.hex())
        else:
            self.entry.config(bg="red")
            setnewvalue("")
        if self.onchanged:
            self.onchanged()

