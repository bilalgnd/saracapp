import os
import re

with open('ui_recovered.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace self.aktif_siparisler with models.aktif_siparisler
text = text.replace('self.aktif_siparisler', 'models.aktif_siparisler')

# 2. Add kuyruk_dinle and global ref to __init__
init_pattern = r'def __init__\(self\):.*?(?=        self.menu_icecekler)'
new_init = '''def __init__(self):
        super().__init__()
        global kasa_arayuz_referansi
        kasa_arayuz_referansi = self

        self.title("SARACOGLU DONER v4.1.3")
        ctk.set_appearance_mode("dark")
        self.geometry("1400x800")
        self.minsize(1300, 700)

        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.arka_plana_gizle)
        keyboard.add_hotkey("ctrl+shift+alt+f2", self.arayuzu_goster_tetikleyici)
        keyboard.add_hotkey("ctrl+alt+s", self.arayuzu_goster_tetikleyici)

        self.after(100, self.kuyruk_dinle)
'''
text = re.sub(init_pattern, new_init, text, flags=re.DOTALL)

# 3. Add kuyruk_dinle method
kuyruk_dinle_code = '''
    def kuyruk_dinle(self):
        import queue
        try:
            while True:
                olay = ui_event_queue.get_nowait()
                if olay["action"] == "siparis_geldi":
                    self.telefondan_siparis_geldi(olay["veri"])
                elif olay["action"] == "silme_geldi":
                    self.telefondan_silme_geldi(olay["veri"])
                elif olay["action"] == "guncelleme_talep_et":
                    telefona_guncelleme_gonder(models.aktif_siparisler)
        except queue.Empty:
            pass
        self.after(100, self.kuyruk_dinle)
'''
text = text.replace('def pc_bildirim_goster', kuyruk_dinle_code + '\n    def pc_bildirim_goster')

# 4. Fix usb_fis_yazdir
usb_pattern = r'usb_fis_yazdir\([^)]+\)'
new_usb = 'fis_yazdir(isim, datetime.datetime.now().strftime("%H:%M"), self.sepet, sum(k["fiyat"] for k in self.sepet))'
text = re.sub(usb_pattern, new_usb, text)

# 5. Fix masalari_diske_kaydet_ve_yay
masalar_pattern = r'def masalari_diske_kaydet_ve_yay\(self\):.*?json_kaydet\(MASALAR_DOSYASI, models\.aktif_siparisler\)'
new_masalar = '''def masalari_diske_kaydet_ve_yay(self):
        json_kaydet(MASALAR_DOSYASI, models.aktif_siparisler)
        telefona_guncelleme_gonder(models.aktif_siparisler)'''
text = re.sub(masalar_pattern, new_masalar, text, flags=re.DOTALL)

# 6. Prepend Imports
imports = '''import customtkinter as ctk
import threading
import keyboard
import json
import time
import datetime
import logging
import webbrowser
import os
import requests
from tkinter import messagebox
from config import *
import models
from models import *
from printer_service import fis_yazdir, get_available_printers, YAZICI_AKTIF
from events import ui_event_queue
from server import telefona_guncelleme_gonder, telefona_ozel_mesaj_gonder

logger = logging.getLogger(__name__)

'''
text = imports + text

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("ui.py successfully rebuilt!")
