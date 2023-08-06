#!/usr/bin/env python3

from tkinter import *
from tkinter.messagebox import showerror
from tkinter import ttk

from .VaultSelector import VaultSelector
from .ValueEntry import ValueEntry

from .FrameVaultTabController import FrameVaultTabController

from ..pubsub import publish, subscribe



class FrameVault(Frame):

    def __init__(self, parent, csv=None, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.vault_selector = VaultSelector(self)
        self.vault_selector.pack(side="top", fill="x", expand=False)

        self.tabs = FrameVaultTabController(self, csv=csv)
        self.tabs.pack(side="top", fill="both", expand=True)

        self.__bind_events()

    def __bind_events(self):
        subscribe("card/vault/status", self.on_vault_status_updated)
        subscribe("error/vault/wrong-password", self.on_wrong_password)

    def on_vault_status_updated(self, status):
        if not status["success"]: return
        active_vault = status["vault"]
        vault_opened = status["open"]

        self.tabs.update_status(vault_open=vault_opened)

    def on_wrong_password(self):
        showerror(title="Error", message="Wrong password or the given vault is not initialized.")
