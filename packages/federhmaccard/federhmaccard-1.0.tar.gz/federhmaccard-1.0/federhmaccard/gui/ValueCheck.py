#!/usr/bin/env python3

from tkinter import BooleanVar, Checkbutton 

class ValueCheck(Checkbutton):

    def __init__(self, parent, *args, **kvargs):
        value = BooleanVar()
        kvargs["variable"] = value
        kvargs["onvalue"] = True
        kvargs["offvalue"] = False

        Checkbutton.__init__(self, parent, *args, **kvargs)
        self.value = value
