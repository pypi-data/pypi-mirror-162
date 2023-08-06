#!/usr/bin/env python3

from tkinter import StringVar, Entry

class ValueEntry(Entry):

    def __init__(self, parent, *args, **kvargs):
        value = StringVar()
        kvargs["textvariable"] = value

        Entry.__init__(self, parent, *args, **kvargs)
        self.value = value
