#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry

import pyperclip

class PasswordResultDisplay(Frame):

    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.columnconfigure(0, weight=1)
    
        self.result = ValueEntry(
            self, state="readonly", font=("monospace", 16), show="*")
        self.result.grid(row=0, column=0, sticky="we", pady=10)

        self.btn_toggle = Button(self, text="Show")
        self.btn_toggle.grid(row=0, column=1, sticky="news", pady=10)
        self.btn_toggle.bind("<Button-1>", self.on_toggle_result)

        self.btn_copy = Button(self, text="Copy")
        self.btn_copy.grid(row=0, column=2, sticky="news", pady=10)
        self.btn_copy.bind("<Button-1>", self.on_copy)

        self.value = self.result.value
        self.__result_in_plain = False

    def on_toggle_result(self, *args):
        self.__result_in_plain = not self.__result_in_plain
        self.result.config(show="" if self.__result_in_plain else "*")
        self.btn_toggle.config(text="Hide" if self.__result_in_plain else "Show")

    def on_copy(self, *args):
        pyperclip.copy(self.result.value.get())

