#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from .PasswordGen import PasswordGen
from .ValueEntry import ValueEntry
from .BinaryValueEntry import BinaryValueEntry
from ..pubsub import publish, subscribe
from ..password_request_uri import FederPRURI, FederPRURIAlgorithm,\
    FederPRURICombinations


class TabPasswordgen(Frame):
    
    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)

        ROW = 0

        self.result = PasswordGen(self, text="Password Generator")
        self.result.grid(
            row=ROW, column=0, columnspan=3, sticky="news",
            padx=10, pady=10, ipadx=10, ipady=10)

        ROW += 1

        self.lbl_salt = Label(self, text="Salt")
        self.lbl_salt.grid(row=ROW, column=0)

        self.lbl_algo = Label(self, text="Algorithm")
        self.lbl_algo.grid(row=ROW, column=1)

        ROW += 1

        self.salt = BinaryValueEntry(self)
        self.salt.grid(row=ROW, column=0, sticky="we")
        self.salt.hexvalue.trace_add("write", self.on_seed_invalidated)

        self.algo = ttk.Combobox(self, values=["SHA1", "SHA256"], state="readonly")
        self.algo.grid(row=ROW, column=1, sticky="we")
        self.algo.current(0)
        self.algo.bind("<FocusOut>", self.on_seed_invalidated)

        self.btn_generate = Button(self, text="Generate")
        self.btn_generate.grid(row=ROW, column=2, sticky="news")
        self.btn_generate.bind("<Button-1>", self.on_generate_clicked)

        ROW += 1

        Label(
            self,
            text="Or, input a Password Request URI (PRU):",
            justify="left"
        ).grid(
            row=ROW,
            column=0, columnspan=2,
            sticky="ew"
        )

        ROW += 1

        self.pru = ValueEntry(self)
        self.pru.grid(row=ROW, column=0, columnspan=2, sticky="ew")
        self.pru.value.trace_add("write", self.on_pru_changed)

        self.btn_pruapply = Button(self, text="Apply")
        self.btn_pruapply.grid(row=ROW, column=2, sticky="news")
        self.btn_pruapply.bind("<Button-1>", self.on_apply_pru)

        self.__bind_events()

    def on_seed_invalidated(self, *args):
        self.result.seed(None)

    def on_generate_clicked(self, *args):
        salt = bytes.fromhex(self.salt.hexvalue.get())
        algo = ["sha1", "sha256"][self.algo.current()]
        publish("card/do/vault/hmac-%s#passwordgen" % algo, salt)

    def on_pru_changed(self, *args):
        self.pru.config(bg="white")

    def on_apply_pru(self, *args):
        try:
            pru = FederPRURI.fromstring(self.pru.get())
        except:
            self.pru.config(bg="red")
            return

        if pru.algorithm == FederPRURIAlgorithm.SHA256:
            self.algo.current(1)
        else:
            self.algo.current(0)

        self.salt.set_bytes_to_hex_value(pru.seed)

        c = pru.combinations
        self.result.charAZ.value.set(
            bool(c & FederPRURICombinations.UPPERCASE.value))
        self.result.charaz.value.set(
            bool(c & FederPRURICombinations.LOWERCASE.value))
        self.result.char09.value.set(
            bool(c & FederPRURICombinations.NUMERICAL.value))
        self.result.charspecial.value.set(
            bool(c & FederPRURICombinations.SPECIAL.value))

    def __bind_events(self):
        subscribe("result/hmac/sha1#passwordgen", self.on_hmac_sha1_result)
        subscribe("result/hmac/sha256#passwordgen", self.on_hmac_sha256_result)

    def on_hmac_sha1_result(self, digest):
        self.__show_result("SHA1", digest)

    def on_hmac_sha256_result(self, digest):
        self.__show_result("SHA256", digest)

    def __show_result(self, algo, digest):
        self.result.seed(digest)
