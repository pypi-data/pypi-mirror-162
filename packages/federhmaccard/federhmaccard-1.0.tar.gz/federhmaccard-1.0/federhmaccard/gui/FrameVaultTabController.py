#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from .ValueEntry import ValueEntry
from ..pubsub import publish, subscribe

from .FrameVaultTabDecrypt import TabDecrypt
from .FrameVaultTabTreeview import TabTreeview
from .FrameVaultTabPasswordgen import TabPasswordgen
from .FrameVaultTabTOTP import TabTOTP
from .FrameVaultTabAdvanced import TabAdvanced


class FrameVaultTabController(ttk.Notebook):

    def __init__(self, parent, csv=None, *args, **kvargs):
        ttk.Notebook.__init__(self, parent, *args, **kvargs)

        #self.tabs = tabs
        #Eself.tabs.pack(side="top", fill="both", expand=True)

        self.has_tree = False
        if csv:
            self.has_tree = True
            self.tab_treeview = TabTreeview(self, csv=csv)

        self.tab_decrypt = TabDecrypt(self)
        self.tab_pwdgen = TabPasswordgen(self)
        self.tab_totp = TabTOTP(self)
        self.tab_advanced = TabAdvanced(self)
        
        self.add(self.tab_decrypt, text="Unlock vault")
        if self.has_tree:
            self.add(self.tab_treeview, text="From codebook")
        self.add(self.tab_pwdgen, text="Password Generator")
        self.add(self.tab_totp, text="Time-based Codes")
        self.add(self.tab_advanced, text="Advanced")
        
        self.update_status()

    def update_status(self, vault_open=False):
        for i in range(0, 4): self.hide(i)
        if not vault_open:
            self.add(self.tab_decrypt)
            self.add(self.tab_advanced)#, text="Advanced")
            self.select(self.tab_decrypt)
        else:
            if self.has_tree:
                self.add(self.tab_treeview)
            self.add(self.tab_pwdgen)#, text="Password Generation")
            self.add(self.tab_totp)
            self.add(self.tab_advanced)#, text="Advanced")
            if self.has_tree:
                self.select(self.tab_treeview)
            else:
                self.select(self.tab_pwdgen)
