#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk

class FrameWaitCard(Frame):

    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.label = Label(self, text="Please insert your FederHMAC card.")
        self.label.pack(fill="both", expand=True)
