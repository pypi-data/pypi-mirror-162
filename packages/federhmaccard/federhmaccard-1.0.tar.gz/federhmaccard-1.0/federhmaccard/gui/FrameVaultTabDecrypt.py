#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry
from ..pubsub import publish, subscribe


class TabDecrypt(Frame):
    
    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)
        
        self.lbl_prompt = Label(self, text="Password:")
        self.lbl_prompt.grid(column=0, row=0, padx=10, pady=20, sticky="e")

        self.txt_password = ValueEntry(self, show="*")
        self.txt_password.grid(column=1, row=0, padx=10, pady=20, sticky="ew")
        self.txt_password.value.set("password")

        self.btn_login = Button(self, text="Decrypt")
        self.btn_login.grid(column=2, row=0, padx=10, pady=20, sticky="ew")
        self.btn_login.bind("<Button-1>", self.on_login_clicked)


    def on_login_clicked(self, *args):
        password = self.txt_password.value.get()
        publish("card/do/vault/open", password)
