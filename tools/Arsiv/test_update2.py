import sys
import threading
import time
sys.path.append('C:/Users/bilal/SARACAPP')
from kasa_app import KasaSistemi
import tkinter as tk

app = KasaSistemi()
app.withdraw()

def my_showerror(title, msg):
    print("ERROR:", title, msg)
    import os; os._exit(1)

import tkinter.messagebox
tkinter.messagebox.showerror = my_showerror

def hook_toplevel(*args, **kwargs):
    print("TOPLEVEL CREATED")
    import os; os._exit(0)

import customtkinter
customtkinter.CTkToplevel = hook_toplevel

app.guncellemeleri_kontrol_et()
app.after(3000, lambda: print("TIMEOUT"))
app.mainloop()
