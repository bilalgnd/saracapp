import codecs

kasa_pyw = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(kasa_pyw, 'r', 'utf-8') as f:
    text = f.read()

# Replace version
text = text.replace('MEVCUT_VERSIYON = "v4.0.1"', 'MEVCUT_VERSIYON = "v4.1.1"')
text = text.replace('ctk.CTkLabel(tepe_kutu, text="v4.0.1"', 'ctk.CTkLabel(tepe_kutu, text="v4.1.1"')
text = text.replace('if tag == "v4.0.1" or tag == "4.0.1":', 'if tag == "v4.1.1" or tag == "4.1.1":')

# Add Muzik Button
btn_code_old = """self.yazici_btn.pack(side="left", padx=3)
        self.kapat_btn = ctk.CTkButton(btn_kutu, text="🚪 Çıkış", font=("Arial", 16, "bold"), fg_color="#1E1E1E", hover_color="#b71c1c", command=self.sistemi_tamamen_kapat, width=70, height=35)"""
btn_code_new = """self.yazici_btn.pack(side="left", padx=3)
        self.muzik_btn = ctk.CTkButton(btn_kutu, text="🎵 TV Müzik", font=("Arial", 16, "bold"), fg_color="#FF0000", hover_color="#CC0000", command=self.muzik_ayari_penceresi, width=70, height=35)
        self.muzik_btn.pack(side="left", padx=3)
        self.kapat_btn = ctk.CTkButton(btn_kutu, text="🚪 Çıkış", font=("Arial", 16, "bold"), fg_color="#1E1E1E", hover_color="#b71c1c", command=self.sistemi_tamamen_kapat, width=70, height=35)"""

text = text.replace(btn_code_old, btn_code_new)

with codecs.open(kasa_pyw, 'w', 'utf-8') as f:
    f.write(text)

print("UI Fixed successfully.")
