#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk

from ..pubsub import publish #, subscribe

class FrameCardUnlock(Frame):

    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        ct = Frame(self)
        self.container = ct 
        self.container.pack(fill="x", expand=True)

        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=3)
        self.container.columnconfigure(2, weight=1)

        self.lbl_prompt = Label(ct, text="Password:")
        self.lbl_prompt.grid(column=0, row=0, padx=10, pady=20, sticky="e")

        self.txt_password = Entry(ct)
        self.txt_password.grid(column=1, row=0, padx=10, pady=20, sticky="ew")

        self.btn_login = Button(ct, text="Login")
        self.btn_login.grid(column=2, row=0, padx=10, pady=20, sticky="ew")
        self.btn_login.bind("<Button-1>", self.do_login)

        self.lbl_reset = Label(ct, text="Dangerous! Do factory reset:", fg="red", anchor="e")
        self.lbl_reset.grid(column=0, columnspan=2, row=1, padx=10, pady=20, sticky="ew")

        self.btn_reset = Button(ct, text="Factory Reset")
        self.btn_reset.grid(column=2, row=1, padx=10, pady=20, sticky="ew")

    def do_login(self, *args):
        password = self.txt_password.get().encode("ascii")
        publish("card/do/login", password)
