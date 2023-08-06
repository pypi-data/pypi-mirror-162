#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry
from .ValueCheck import ValueCheck
from .PasswordResultDisplay import PasswordResultDisplay
from ..seed_to_password import seed2password



LENGTHS = [8, 12, 16, 20, 24, 28, 32, 64, 128]
class PasswordGen(ttk.LabelFrame):

    def __init__(self, parent, *args, **kvargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kvargs)

        self.__seed = None
        self.__result_in_plain = False

        for i in range(1, 5): self.columnconfigure(i, weight=1)

        ROW = 0

        self.result = PasswordResultDisplay(self)
        self.result.grid(row=ROW, column=0, columnspan=5, sticky="news")

        ROW += 1

        Label(self, text="Length").grid(row=ROW, column=0, sticky="news")
        Label(self, text="A-Z").grid(row=ROW, column=1, sticky="news")
        Label(self, text="a-z").grid(row=ROW, column=2, sticky="news")
        Label(self, text="0-9").grid(row=ROW, column=3, sticky="news")
        Label(self, text="*#?").grid(row=ROW, column=4, sticky="news")

        ROW += 1
            
        self.pwdlength = ttk.Combobox(
            self, values=[str(e) for e in LENGTHS], state="readonly")
        self.pwdlength.current(3)
        self.pwdlength.grid(row=ROW, column=0, sticky="news")

        self.charAZ = ValueCheck(self)
        self.charAZ.grid(row=ROW, column=1, sticky="news")
        self.charAZ.value.set(True)

        self.charaz = ValueCheck(self)
        self.charaz.grid(row=ROW, column=2, sticky="news")
        self.charaz.value.set(True)

        self.char09 = ValueCheck(self)
        self.char09.grid(row=ROW, column=3, sticky="news")
        self.char09.value.set(True)

        self.charspecial = ValueCheck(self)
        self.charspecial.grid(row=ROW, column=4, sticky="news")
        self.charspecial.value.set(True)

        for e in [
            self.pwdlength, self.charaz,
            self.charAZ, self.char09, self.charspecial
        ]:
            e.bind("<ButtonRelease>", self.update_result)
            e.bind("<Key>", self.update_result)
        self.pwdlength.bind("<<ComboboxSelected>>", self.update_result)

    def seed(self, s):
        self.__seed = s 
        self.update_result()

    def update_result(self, *args):
        if not self.__seed: return self.result.value.set("")

        password = seed2password(
            seed = self.__seed,
            length = LENGTHS[self.pwdlength.current()],
            az = self.charaz.value.get(),
            AZ = self.charAZ.value.get(),
            num = self.char09.value.get(),
            special = self.charspecial.value.get()
        )
        
        self.result.value.set(password)
