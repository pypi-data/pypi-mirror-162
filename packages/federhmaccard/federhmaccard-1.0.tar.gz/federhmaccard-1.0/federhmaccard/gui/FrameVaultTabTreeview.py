#!/usr/bin/env python3

#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from ..pubsub import publish, subscribe
from ..password_request_uri import FederPRURI, FederPRURIAlgorithm,\
    FederPRURICombinations
from .PasswordTreeview import PasswordTreeview
from .PasswordResultDisplay import PasswordResultDisplay
from ..seed_to_password import seed2password
from ..password_request_uri import FederPRURI


class TabTreeview(Frame):
    
    def __init__(self, parent, csv=None, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.treeview = PasswordTreeview(self, csv=csv)
        self.treeview.grid(row=0, column=0, sticky="news")

        self.result = PasswordResultDisplay(self)
        self.result.grid(row=1, column=0, sticky="news")

        self.__old_sel = None
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_selected)
        self.treeview.value.trace_add("write", self.on_treeview_changed)
        self.__bind_events()

    def on_treeview_selected(self, *args):
        if self.__old_sel == self.treeview.selection():
            return
        self.__show_result(None)
        self.__old_sel = self.treeview.selection()

    def on_treeview_changed(self, *args):
        try:
            pruri = FederPRURI.fromstring(self.treeview.value.get())
        except Exception as e:
            print(e)
            return
        self.passwordgen_kvargs = {
            "length": pruri.length,
            "az": pruri.combinations & FederPRURICombinations.LOWERCASE.value,
            "AZ": pruri.combinations & FederPRURICombinations.UPPERCASE.value,
            "num": pruri.combinations & FederPRURICombinations.NUMERICAL.value,
            "special": pruri.combinations & FederPRURICombinations.SPECIAL.value,
        }
        cmd = "card/do/vault/hmac-%s#codebook" % (
            'sha1' if pruri.algorithm == FederPRURIAlgorithm.SHA1 else 'sha256')
        publish(cmd, pruri.seed)

    def __bind_events(self):
        subscribe("result/hmac/sha1#codebook", self.on_hmac_sha1_result)
        subscribe("result/hmac/sha256#codebook", self.on_hmac_sha256_result)

    def on_hmac_sha1_result(self, digest):
        self.__show_result(digest)

    def on_hmac_sha256_result(self, digest):
        self.__show_result(digest)

    def __show_result(self, digest):
        if not digest: return self.result.value.set("")

        password = seed2password(
            seed = digest,
            **self.passwordgen_kvargs)
        self.result.value.set(password)
