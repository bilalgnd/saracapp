import os
import codecs
import re

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Replace version
text = text.replace('4.0.6', '4.0.7')

# UI generation block
old_ui = '''            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                b, _ = cip_olustur(cik_sat, f"{ad} Yok", var, "#E53935", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_ekle, ekle_btns))
                b.grid(row=i//6, column=i%6, padx=5, pady=5)
                cikar_btns.append((ad, b, var))'''

new_ui = '''            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                cik_ad = ad + "siz" if ad != "Tursu" else "Tursusuz"
                b, _ = cip_olustur(cik_sat, cik_ad, var, "#E53935", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_ekle, ekle_btns))
                b.grid(row=i//6, column=i%6, padx=5, pady=5)
                cikar_btns.append((ad, b, var))'''

text = text.replace(old_ui, new_ui)

# Basket text block
old_basket = '''        n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])'''
new_basket = '''        n.extend([k + "siz" if k != "Tursu" else "Tursusuz" for k, v in self.modal_cikar.items() if v.get()])'''

text = text.replace(old_basket, new_basket)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)

print("Updated kasa_app.pyw logic and version")
