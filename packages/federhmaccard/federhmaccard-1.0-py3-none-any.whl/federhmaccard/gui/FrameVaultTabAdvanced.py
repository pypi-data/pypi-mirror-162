#!/usr/bin/env python3

import base64
import re

from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog

from .ValueEntry import ValueEntry
from .BinaryValueEntry import BinaryValueEntry
from .CustomizedLabelFrame import CustomizedLabelFrame
from ..pubsub import publish, subscribe

IMPORT_FORMATS = ["ASCII", "HEX", "Base32", "Base64"]


class TabAdvanced(Frame):
    
    def __init__(self, parent, *args, **kvargs):
        Frame.__init__(self, parent, *args, **kvargs)

        self.frame_import = CustomizedLabelFrame(self, text="Import secret")

        self.frame_import.columnconfigure(0, weight=1)
        self.frame_import.columnconfigure(1, weight=1)
        self.frame_import.columnconfigure(2, weight=1)

        self.lbl_import_warning = Label(
            self.frame_import,
            text="Warning: this will overwrite existing secret!"
        )
        self.lbl_import_warning.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.import_secret = BinaryValueEntry(self.frame_import)
        self.import_secret.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.import_desc = Label(self.frame_import, text="\n".join([
            "Notes:",
            "1. This operation will write a secret to the vault. ",
            "The written secret is not retractable from the vault.",
            "2. Any existing secret in this vault will be lost. ",
            "If you have no backup of that secret, do not import!",
            "3. If you intend to use the vault for TOTP based verification",
            " codes, you may need to select Base32 encoding."
        ]))
        self.import_desc.grid(row=2, column=0, columnspan=3, sticky="news")

        self.btn_import = Button(self.frame_import, text="Import")
        self.btn_import.grid(row=3, column=1, sticky="ew")
        self.btn_import.bind("<Button-1>", self.on_import_secret)
        
        self.frame_import.pack(side="top", fill="x", expand=False)
        subscribe("error/vault/failed-import", self.on_import_failure)
        subscribe("result/import/ok", self.on_import_ok)

        # change password frame

        self.frame_pwd = CustomizedLabelFrame(self, text="Change password")
        self.frame_pwd.pack(side="top", fill="x", expand=False)
        self.frame_pwd.enable(False)

        Label(
            self.frame_pwd,
            text="To change the password of this vault, click here."
        ).pack(side="left")

        self.btn_pwd = Button(self.frame_pwd, text="Change password...")
        self.btn_pwd.pack(side="left")
        self.btn_pwd.bind("<Button-1>", self.on_change_password)

        subscribe("error/vault/failed-reencrypt", self.on_reencrypt_failure)
        subscribe("result/reencrypt/ok", self.on_reencrypt_ok)
        subscribe("card/vault/status", self.on_vault_status)

    def on_vault_status(self, status):
        print("adv", status)
        try:
            if status["success"] and status["open"]:
                self.frame_pwd.enable(True)
                self.frame_import.enable(False)
                return
        except Exception as e:
            print(e)
        self.frame_pwd.enable(False)
        self.frame_import.enable(True)

    def on_import_failure(self, *args):
        messagebox.showerror("Error", "Failed to import secret.")

    def on_import_ok(self, *args):
        messagebox.showinfo("Success", "Vault initialized with new secret.")
        self.import_secret.value.set("")

    def on_import_secret(self, *args):
        newsecret = None
        try:
            newsecret = bytes.fromhex(self.import_secret.hexvalue.get())
        except:
            pass

        if not newsecret:
            messagebox.showerror("Error", "Cannot import empty secret.")
            return
        if messagebox.askquestion("Confirm", "This will overwrite any secret on card! Are you sure to continue?") != "yes":
            return
        if simpledialog.askstring("Confirm again", "Type the word CONFIRM in uppercase to continue.", parent=self) != "CONFIRM":
            return

        self.import_secret.clear()
        publish("card/do/vault/import", newsecret)
        

    def on_change_password(self, *args):
        pwd1 = simpledialog.askstring(
            "Change password", "Enter new password:", show='*')
        if pwd1 == None:
            messagebox.showinfo("Abort", "Password not changed.")
            return
        pwd2 = simpledialog.askstring(
            "Confirm password", "Enter your password again:", show='*')
        if pwd2 == None:
            messagebox.showinfo("Abort", "Password not changed.")
            return
        if pwd2 != pwd1:
            messagebox.showerror(
                "Abort", "Two input of passwords do not match.")
            return

        publish("card/do/vault/reencrypt", pwd2)

    def on_reencrypt_ok(self, *args):
        messagebox.showinfo("Success", "Vault password changed.")

    def on_reencrypt_failure(self, *args):
        messagebox.showinfo("Error", "Failed changing vault password.")
