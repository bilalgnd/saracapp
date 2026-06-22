import codecs
import json

kasa_pyw = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(kasa_pyw, 'r', 'utf-8') as f:
    text = f.read()

# Version bumps
text = text.replace("4.1.0", "4.1.1")

# Route for /tv_settings
route_code = """@flask_app.route('/tv')
def tv_sayfa():
    return render_template('tv.html')

@flask_app.route('/tv_settings')
def tv_settings():
    return jsonify({"youtube_url": SISTEM_AYARLARI.get("YOUTUBE_LINK", "")})
"""

text = text.replace("@flask_app.route('/tv')\r\ndef tv_sayfa():\r\n    return render_template('tv.html')", route_code)
text = text.replace("@flask_app.route('/tv')\ndef tv_sayfa():\n    return render_template('tv.html')", route_code)

# Button addition
btn_code_old = """self.yazici_btn = ctk.CTkButton(btn_kutu, text="🖨️ Yazici", font=("Arial", 16, "bold"), fg_color="#424242", command=self.yazici_ayari_penceresi, width=70, height=35)
        self.yazici_btn.pack(side="left", padx=3)"""

btn_code_new = """self.yazici_btn = ctk.CTkButton(btn_kutu, text="🖨️ Yazici", font=("Arial", 16, "bold"), fg_color="#424242", command=self.yazici_ayari_penceresi, width=70, height=35)
        self.yazici_btn.pack(side="left", padx=3)
        self.muzik_btn = ctk.CTkButton(btn_kutu, text="🎵 TV Müzik", font=("Arial", 16, "bold"), fg_color="#FF0000", hover_color="#CC0000", command=self.muzik_ayari_penceresi, width=70, height=35)
        self.muzik_btn.pack(side="left", padx=3)"""

text = text.replace(btn_code_old, btn_code_new)

# Function addition
popup_func = """    def muzik_ayari_penceresi(self):
        popup = ctk.CTkToplevel(self)
        popup.title("TV Müzik Ayari")
        popup.geometry("500x250")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="YouTube Video veya Playlist Linki:", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        
        link_var = ctk.StringVar(value=SISTEM_AYARLARI.get("YOUTUBE_LINK", ""))
        link_entry = ctk.CTkEntry(popup, textvariable=link_var, font=("Arial", 16), width=450)
        link_entry.pack(pady=10)

        durum_lbl = ctk.CTkLabel(popup, text="", font=("Arial", 14), text_color="green")
        
        def kaydet():
            val = link_var.get().strip()
            SISTEM_AYARLARI["YOUTUBE_LINK"] = val
            json_kaydet(AYAR_DOSYASI, SISTEM_AYARLARI)
            durum_lbl.configure(text="YouTube Linki Başarıyla Kaydedildi!")
            popup.after(1500, popup.destroy)
            
        ctk.CTkButton(popup, text="Kaydet", font=("Arial", 16, "bold"), fg_color="#FF0000", hover_color="#CC0000", command=kaydet).pack(pady=15)
        durum_lbl.pack(pady=5)

    def yazici_ayari_penceresi(self):"""

text = text.replace("    def yazici_ayari_penceresi(self):", popup_func)

with codecs.open(kasa_pyw, 'w', 'utf-8') as f:
    f.write(text)

# HTML and Android bump
def bump(filepath, old_str, new_str):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        t = f.read()
    t = t.replace(old_str, new_str)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(t)

bump('C:/Users/bilal/SARACAPP/templates/index.html', '4.1.0', '4.1.1')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', '4.1.0', '4.1.1')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionName = "4.1.0"', 'versionName = "4.1.1"')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionCode = 4100', 'versionCode = 4110')

print("Modifications applied successfully.")
