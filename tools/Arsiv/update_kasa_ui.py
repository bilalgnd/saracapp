import codecs
import re

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Product colors in sekmeleri_olustur
colors_pattern = r'            ad_kucuk = urun\[\'ad\'\].lower\(\).*?else: bg_renk = "#37474F" if self\.ayarlar_modu else "#1E1E1E"; txt_renk = "white"; hov_renk = "#455A64" if self\.ayarlar_modu else "#333333"'

new_colors = '''            ad_kucuk = urun['ad'].replace('İ','i').replace('I','ı').lower()
            if "tombik" in ad_kucuk: bg_renk = "#FF9800"; txt_renk = "black"; hov_renk = "#F57C00"
            elif "eski usul" in ad_kucuk: bg_renk = "#F44336"; txt_renk = "white"; hov_renk = "#D32F2F"
            elif "d" in ad_kucuk and "r" in ad_kucuk and "m" in ad_kucuk and len(ad_kucuk) < 7: bg_renk = "#FFEB3B"; txt_renk = "black"; hov_renk = "#FBC02D"
            elif any(x in ad_kucuk for x in ["et porsiyon", "beyti", "iskender", "ıskender"]) or ("pilav üstü" in ad_kucuk and "tavuk" not in ad_kucuk): bg_renk = "#8B0000"; txt_renk = "white"; hov_renk = "#B71C1C"
            elif "hatay" in ad_kucuk: bg_renk = "#F5DEB3"; txt_renk = "black"; hov_renk = "#D2B48C"
            elif "biga" in ad_kucuk: bg_renk = "#1976D2"; txt_renk = "white"; hov_renk = "#1565C0"
            elif "tavuk porsiyon" in ad_kucuk or ("pilav üstü" in ad_kucuk and "tavuk" in ad_kucuk): bg_renk = "#FFFF5722"; txt_renk = "black"; hov_renk = "#E64A19"
            elif any(x in ad_kucuk for x in ["kola", "ayran", "su", "soda", "sprite", "fanta", "salgam", "zero"]): bg_renk = "#0277BD"; txt_renk = "white"; hov_renk = "#01579B"
            else: bg_renk = "#37474F" if self.ayarlar_modu else "#1E1E1E"; txt_renk = "white"; hov_renk = "#455A64" if self.ayarlar_modu else "#333333"'''

text = re.sub(colors_pattern, lambda m: new_colors, text, flags=re.DOTALL)

# 2. Update Window Title
text = text.replace('self.title("saracapp")', 'self.title("SARAÇOĞLU DÖNER v4.0.5")')


# 3. siparis_penceresi_ac logic
old_vars = '''        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu"]}
        self.modal_ucretli_ek = {e: ctk.BooleanVar(value=False) for e in UCRETLI_EKSTRALAR.keys()}
        self.modal_ucretsiz_ek = {e: ctk.BooleanVar(value=False) for e in ["Sade Et", "Soslu", "Gemi", "Kayık"]}'''
new_vars = '''        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu"]}
        self.modal_ekle = {m: ctk.BooleanVar(value=False) for m in ["Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu"]}
        self.modal_ucretli_ek = {e: ctk.BooleanVar(value=False) for e in UCRETLI_EKSTRALAR.keys()}
        self.modal_ucretsiz_ek = {e: ctk.BooleanVar(value=False) for e in ["Sade Et", "Soslu", "Gemi", "Kayık"]}'''
text = text.replace(old_vars, new_vars)

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

old_ui_sections = '''        if not is_icecek:
            ctk.CTkLabel(govde, text="İçerik Çıkar:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            cik_sat = ctk.CTkFrame(govde, fg_color="transparent"); cik_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                b, _ = cip_olustur(cik_sat, f"{ad} Yok", var, "#D32F2F", "#333333")
                b.grid(row=i//4, column=i%4, padx=5, pady=5)

            ctk.CTkLabel(govde, text="Ücretli Ekstralar:", font=("Arial", 18, "bold"), text_color="#FFD54F").pack(anchor="w", padx=10, pady=(20, 5))
            ek_sat = ctk.CTkFrame(govde, fg_color="transparent"); ek_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_ucretli_ek.items()):
                b, _ = cip_olustur(ek_sat, f"{ad} (+{UCRETLI_EKSTRALAR[ad]}₺)", var, "#FBC02D", "#333333", "black", 180)
                b.grid(row=i//4, column=i%4, padx=5, pady=5)'''
new_ui_sections = '''        if not is_icecek:
            self.icerik_butonlari = []
            def m_exclusive(ad, karsi_dict, b2_list):
                if karsi_dict[ad].get():
                    karsi_dict[ad].set(False)
                    for b2_ad, b2_btn, b2_var in b2_list:
                        if b2_ad == ad:
                            b2_btn.configure(fg_color="#333333")

            ctk.CTkLabel(govde, text="İçerik:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            cik_sat = ctk.CTkFrame(govde, fg_color="transparent"); cik_sat.pack(fill="x", padx=10)
            
            cikar_btns = []
            ekle_btns = []
            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                b, _ = cip_olustur(cik_sat, f"{ad} Yok", var, "#E53935", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_ekle, ekle_btns))
                b.grid(row=i//6, column=i%6, padx=5, pady=5)
                cikar_btns.append((ad, b, var))
            
            for i, (ad, var) in enumerate(self.modal_ekle.items()):
                ek_ad = ad + "lı" if not ad.endswith("es") else ad + "li"
                if ad == "Turşu": ek_ad = "Turşulu"
                b, _ = cip_olustur(cik_sat, ek_ad, var, "#4CAF50", "#333333", on_click=lambda a=ad: m_exclusive(a, self.modal_cikar, cikar_btns))
                b.grid(row=2+i//6, column=i%6, padx=5, pady=5)
                ekle_btns.append((ad, b, var))
            
            c_idx = len(self.modal_ekle)
            for i, malz in enumerate(["Cheddar", "Kasarli", "Kaşarlı"]):
                if malz in self.modal_ucretli_ek:
                    b, _ = cip_olustur(cik_sat, malz.replace("Kasarli", "Kaşarlı"), self.modal_ucretli_ek[malz], "#FFD54F", "#333333", "black")
                    b.grid(row=4, column=i, padx=5, pady=5)

            diger_ucretliler = {k: v for k, v in self.modal_ucretli_ek.items() if k not in ["Cheddar", "Kasarli", "Kaşarlı"]}
            if diger_ucretliler:
                ctk.CTkLabel(govde, text="Ücretli Ekstralar:", font=("Arial", 18, "bold"), text_color="#FFD54F").pack(anchor="w", padx=10, pady=(20, 5))
                ek_sat = ctk.CTkFrame(govde, fg_color="transparent"); ek_sat.pack(fill="x", padx=10)
                for i, (ad, var) in enumerate(diger_ucretliler.items()):
                    b, _ = cip_olustur(ek_sat, f"{ad} (+{UCRETLI_EKSTRALAR[ad]}₺)", var, "#FBC02D", "#333333", "black", 180)
                    b.grid(row=i//4, column=i%4, padx=5, pady=5)'''
text = text.replace(old_ui_sections, new_ui_sections)

old_ic_sat = '''            for i, ic in enumerate(self.menu_icecekler):
                isim = ic['ad']; fy = ic['secenekler'][0]['fiyat']; fy_yz = f"(+{fy}₺)" if fy > 0 else ""
                k = ctk.CTkFrame(ic_sat, fg_color="#1E1E1E", corner_radius=10); k.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
                ctk.CTkLabel(k, text=f"{isim} {fy_yz}", font=("Arial", 18, "bold")).pack(side="left", padx=15)
                var = self.modal_icecek[isim]
                
                a_kt = ctk.CTkFrame(k, fg_color="#333333", corner_radius=8); a_kt.pack(side="right", padx=10, pady=5)
                def d(v=var, y=-1): v.set(max(0, v.get() + y)); self.guncelle_fiyat(popup)
                ctk.CTkButton(a_kt, text="-", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, -1)).pack(side="left")
                l = ctk.CTkLabel(a_kt, text="0", font=("Arial", 20, "bold"), width=30); l.pack(side="left")
                var.trace_add("write", lambda *args, lbl=l, v=var: lbl.configure(text=str(v.get()), text_color="#FF9800" if v.get()>0 else "white"))
                ctk.CTkButton(a_kt, text="+", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, 1)).pack(side="left")'''
new_ic_sat = '''            self.ic_frames = []
            for i, ic in enumerate(self.menu_icecekler):
                isim = ic['ad']; fy = ic['secenekler'][0]['fiyat']; fy_yz = f"(+{fy}₺)" if fy > 0 else ""
                
                ic_ad = isim.lower().replace("ş", "s").replace("ı", "i").replace("ç", "c")
                if "kutu kola" in ic_ad or "sise kola" in ic_ad: bg_c = "#F40009"
                elif "sprite" in ic_ad: bg_c = "#008B47"
                elif "fanta" in ic_ad: bg_c = "#F58216"
                elif "ayran" in ic_ad: bg_c = "#FDFD96"
                elif "su" in ic_ad and "usul" not in ic_ad: bg_c = "#00BFFF"
                elif "soda" in ic_ad: bg_c = "#006400"
                elif "salgam" in ic_ad: bg_c = "#800080"
                elif "zero" in ic_ad: bg_c = "#111111"
                else: bg_c = "#1E1E1E"
                
                yazi_c = "black" if bg_c == "#FDFD96" else "white"
                def get_bg(v, base_c): return base_c if v > 0 else "#2A2A2A"

                var = self.modal_icecek[isim]
                k = ctk.CTkFrame(ic_sat, fg_color=get_bg(var.get(), bg_c), corner_radius=10); k.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
                lbl_ic = ctk.CTkLabel(k, text=f"{isim} {fy_yz}", font=("Arial", 18, "bold"), text_color=yazi_c if var.get()>0 else "white")
                lbl_ic.pack(side="left", padx=15)
                
                self.ic_frames.append((k, lbl_ic, var, bg_c, yazi_c))
                
                a_kt = ctk.CTkFrame(k, fg_color="#333333", corner_radius=8); a_kt.pack(side="right", padx=10, pady=5)
                def d(v=var, y=-1): v.set(max(0, v.get() + y)); self.guncelle_fiyat(popup)
                ctk.CTkButton(a_kt, text="-", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, -1)).pack(side="left")
                l = ctk.CTkLabel(a_kt, text="0", font=("Arial", 20, "bold"), width=30); l.pack(side="left")
                
                def on_ic_change(*args, lbl=l, v=var, f_k=k, f_lbl=lbl_ic, f_bg=bg_c, f_txt=yazi_c):
                    lbl.configure(text=str(v.get()), text_color="white" if v.get()>0 else "white")
                    a_kt.configure(fg_color="#F44336" if v.get()>0 else "#333333")
                    f_k.configure(fg_color=get_bg(v.get(), f_bg))
                    f_lbl.configure(text_color=f_txt if v.get()>0 else "white")
                
                var.trace_add("write", on_ic_change)
                on_ic_change() # trigger manually for initial state
                
                ctk.CTkButton(a_kt, text="+", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, 1)).pack(side="left")'''
text = text.replace(old_ic_sat, new_ic_sat)

old_sepete = '''        n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])
        n.extend([k for k, v in self.modal_ucretsiz_ek.items() if v.get()])
        n.extend([f"{k} eklendi" for k, v in self.modal_ucretli_ek.items() if v.get()])'''
new_sepete = '''        n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])
        for k, v in self.modal_ekle.items():
            if v.get():
                ek_ad = k + "lı" if not k.endswith("es") else k + "li"
                if k == "Turşu": ek_ad = "Turşulu"
                n.append(ek_ad)
        n.extend([k for k, v in self.modal_ucretsiz_ek.items() if v.get()])
        n.extend([f"{k}" for k, v in self.modal_ucretli_ek.items() if v.get() if k in ["Cheddar", "Kasarli", "Kaşarlı"]])
        n.extend([f"{k} eklendi" for k, v in self.modal_ucretli_ek.items() if v.get() if k not in ["Cheddar", "Kasarli", "Kaşarlı"]])'''
text = text.replace(old_sepete, new_sepete)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Updated kasa_app.pyw UI logic successfully.")
