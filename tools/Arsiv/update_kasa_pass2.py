import codecs
import re

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Fix Modal Vars
old_vars = '''        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Sogan", "Domates", "Patates", "Ketçap", "Mayonez", "Tursu"]}'''
if old_vars not in text: old_vars = '''        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Sogan", "Domates", "Patates", "Ket\xc3\xa7ap", "Mayonez", "Tursu"]}'''
new_vars = '''        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Sogan", "Domates", "Patates", "Ketcap", "Mayonez", "Tursu"]}
        self.modal_ekle = {m: ctk.BooleanVar(value=False) for m in ["Sogan", "Domates", "Patates", "Ketcap", "Mayonez", "Tursu"]}'''
# Just replace blindly using regex if we can't find it
text = re.sub(r'self\.modal_cikar = \{m: ctk\.BooleanVar\(value=False\) for m in \[.*?\]\}', new_vars, text)

# Fix cip_olustur
old_cip = '''        def cip_olustur(parent, metin, var, true_color, false_color, yazi_renk="white", genislik=140, on_click=None):
            def toggle():
                if isinstance(var, ctk.BooleanVar): var.set(not var.get())
                elif isinstance(var, ctk.StringVar): var.set(metin)
                btn.configure(fg_color=true_color if (var.get() == True or var.get() == metin) else false_color)
                if on_click: on_click()
                self.guncelle_fiyat(popup) 
            
            btn = ctk.CTkButton(parent, text=metin, font=("Arial", 18, "bold"), width=genislik, height=50, fg_color=true_color if (var.get() == True or var.get() == metin) else false_color, text_color=yazi_renk, corner_radius=10, command=toggle)
            return btn, toggle'''
new_cip = '''        def cip_olustur(parent, metin, var, true_color, false_color, yazi_renk="white", genislik=140, on_click=None):
            def toggle():
                if isinstance(var, ctk.BooleanVar): var.set(not var.get())
                elif isinstance(var, ctk.StringVar): var.set(metin)
                if on_click: on_click()
                btn.configure(fg_color=true_color if (var.get() == True or var.get() == metin) else false_color)
                self.guncelle_fiyat(popup) 
            
            btn = ctk.CTkButton(parent, text=metin, font=("Arial", 18, "bold"), width=genislik, height=50, fg_color=true_color if (var.get() == True or var.get() == metin) else false_color, text_color=yazi_renk, corner_radius=10, command=toggle)
            return btn, toggle'''
text = text.replace(old_cip, new_cip)

# Fix UI Sections
# We use regex to find the `if not is_icecek:` block until `Hızlı İçecek:`
ui_start = text.find('        if not is_icecek:')
ui_end = text.find('ctk.CTkLabel(govde, text="Hızlı İçecek:"', ui_start)
if ui_end == -1: ui_end = text.find('ctk.CTkLabel(govde, text="Hizli Icecek:"', ui_start)
if ui_end == -1: ui_end = text.find('ctk.CTkLabel(govde, text="H', ui_start) # Fallback

new_ui_sections = '''        if not is_icecek:
            def m_exclusive(ad, karsi_dict, b2_list):
                if karsi_dict[ad].get():
                    karsi_dict[ad].set(False)
                    for b2_ad, b2_btn, b2_var in b2_list:
                        if b2_ad == ad:
                            b2_btn.configure(fg_color="#333333")

            ctk.CTkLabel(govde, text="Icerik:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            cik_sat = ctk.CTkFrame(govde, fg_color="transparent"); cik_sat.pack(fill="x", padx=10)
            
            cikar_btns = []
            ekle_btns = []
            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                b, _ = cip_olustur(cik_sat, f"{ad} Yok", var, "#E53935", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_ekle, ekle_btns))
                b.grid(row=i//6, column=i%6, padx=5, pady=5)
                cikar_btns.append((ad, b, var))
            
            for i, (ad, var) in enumerate(self.modal_ekle.items()):
                ek_ad = ad + "li" if not ad.endswith("es") else ad + "li"
                if ad == "Tursu": ek_ad = "Tursulu"
                if ad == "Sogan": ek_ad = "Soganli"
                if ad == "Ketcap": ek_ad = "Ketcapli"
                b, _ = cip_olustur(cik_sat, ek_ad, var, "#4CAF50", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_cikar, cikar_btns))
                b.grid(row=2+i//6, column=i%6, padx=5, pady=5)
                ekle_btns.append((ad, b, var))
            
            for i, malz in enumerate(["Cheddar", "Kasarli"]):
                if malz in self.modal_ucretli_ek:
                    b, _ = cip_olustur(cik_sat, malz, self.modal_ucretli_ek[malz], "#FFD54F", "#333333", "black")
                    b.grid(row=4, column=i, padx=5, pady=5)

            diger_ucretliler = {k: v for k, v in self.modal_ucretli_ek.items() if k not in ["Cheddar", "Kasarli"]}
            if diger_ucretliler:
                ctk.CTkLabel(govde, text="Ucretli Ekstralar:", font=("Arial", 18, "bold"), text_color="#FFD54F").pack(anchor="w", padx=10, pady=(20, 5))
                ek_sat = ctk.CTkFrame(govde, fg_color="transparent"); ek_sat.pack(fill="x", padx=10)
                for i, (ad, var) in enumerate(diger_ucretliler.items()):
                    b, _ = cip_olustur(ek_sat, f"{ad} (+{UCRETLI_EKSTRALAR[ad]} TL)", var, "#FBC02D", "#333333", "black", 180)
                    b.grid(row=i//4, column=i%4, padx=5, pady=5)

            ctk.CTkLabel(govde, text="Notlar:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            not_sat = ctk.CTkFrame(govde, fg_color="transparent"); not_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_ucretsiz_ek.items()):
                b, _ = cip_olustur(not_sat, ad, var, "#757575", "#333333")
                b.grid(row=i//4, column=i%4, padx=5, pady=5)

            '''
            
if ui_start != -1 and ui_end != -1:
    text = text[:ui_start] + new_ui_sections + text[ui_end:]


# Fix sepete ekle array
sepete_start = text.find('n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])')
sepete_end = text.find('        if self.modal_ozel_not.get().strip():', sepete_start)

new_sepete = '''n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])
        for k, v in self.modal_ekle.items():
            if v.get():
                ek_ad = k + "li" if not k.endswith("es") else k + "li"
                if k == "Tursu": ek_ad = "Tursulu"
                if k == "Sogan": ek_ad = "Soganli"
                if k == "Ketcap": ek_ad = "Ketcapli"
                n.append(ek_ad)
        n.extend([k for k, v in self.modal_ucretsiz_ek.items() if v.get()])
        n.extend([f"{k}" for k, v in self.modal_ucretli_ek.items() if v.get() if k in ["Cheddar", "Kasarli"]])
        n.extend([f"{k} eklendi" for k, v in self.modal_ucretli_ek.items() if v.get() if k not in ["Cheddar", "Kasarli"]])
'''

if sepete_start != -1 and sepete_end != -1:
    text = text[:sepete_start] + new_sepete + text[sepete_end:]

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)

print("Pass 2: Update modal vars and logic UI.")
