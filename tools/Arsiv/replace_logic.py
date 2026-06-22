import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    text = f.read()

# Replace version label
text = text.replace('text="v3.0.3"', 'text="v4.0.1"')

# Add MEVCUT_VERSIYON
if 'MEVCUT_VERSIYON =' not in text:
    text = text.replace('PORT = 5000', 'PORT = 5000\nMEVCUT_VERSIYON = "v4.0.1"')

# Replace guncellemeleri_kontrol_et
import re
pattern = r'def guncellemeleri_kontrol_et\(self\):.*?self\.after\(0, lambda: messagebox\.showinfo.*?\)\s*'
new_func = '''def guncellemeleri_kontrol_et(self):
        def islem():
            try:
                response = requests.get("https://api.github.com/repos/bilalgnd/saracapp/releases/latest", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tag = data.get("tag_name", "")
                    assets = data.get("assets", [])
                    apk_url = None
                    exe_url = None
                    for a in assets:
                        if a.get("name", "").endswith(".apk"): apk_url = a.get("browser_download_url")
                        if a.get("name", "").endswith(".exe"): exe_url = a.get("browser_download_url")
                    
                    def arayuz_sor():
                        panel = ctk.CTkToplevel(self)
                        panel.title("Guncelleme Yoneticisi")
                        w, h = 450, 320
                        x = (self.winfo_screenwidth() - w) // 2
                        y = (self.winfo_screenheight() - h) // 2
                        panel.geometry(f"{w}x{h}+{x}+{y}")
                        panel.attributes("-topmost", True)
                        panel.grab_set()
                        
                        if tag == "v4.0.1" or tag == "4.0.1":
                            ctk.CTkLabel(panel, text=f"Versiyon Guncel ({tag})", font=("Arial", 22, "bold"), text_color="#2196F3").pack(pady=20)
                            ctk.CTkLabel(panel, text="Sisteminiz zaten en guncel surumde.", font=("Arial", 16)).pack(pady=20)
                            ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=15, padx=20, fill="x")
                        else:
                            if not apk_url and not exe_url:
                                ctk.CTkLabel(panel, text=f"Versiyon Guncel", font=("Arial", 22, "bold"), text_color="#2196F3").pack(pady=20)
                                ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=15, padx=20, fill="x")
                                return
                                
                            ctk.CTkLabel(panel, text=f"Yeni Versiyon Bulundu: {tag}", font=("Arial", 22, "bold"), text_color="#4CAF50").pack(pady=20)
                            
                            def exe_indir():
                                import webbrowser
                                if exe_url: webbrowser.open(exe_url)
                            
                            def mobile_yolla():
                                if apk_url:
                                    try: telefona_ozel_mesaj_gonder({"type": "apk_guncelleme", "url": apk_url})
                                    except: pass
                                    durum_lbl.configure(text="Garsonlara bildirim basariyla yollandi!", text_color="#FFEB3B")
                            
                            if exe_url:
                                ctk.CTkButton(panel, text="PC Exe Indir (Tarayicida)", font=("Arial", 16, "bold"), command=exe_indir, height=45).pack(pady=10, padx=20, fill="x")
                            if apk_url:
                                ctk.CTkButton(panel, text="Garsonlara APK Gonder", font=("Arial", 16, "bold"), fg_color="#F44336", hover_color="#D32F2F", command=mobile_yolla, height=45).pack(pady=10, padx=20, fill="x")
                            
                            durum_lbl = ctk.CTkLabel(panel, text="", font=("Arial", 15, "bold"))
                            durum_lbl.pack(pady=5)
                                
                            ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=5, padx=20, fill="x")
                            
                    self.after(0, arayuz_sor)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", f"Baglanti hatasi: {e}"))
        threading.Thread(target=islem, daemon=True).start()
'''

text = re.sub(pattern, new_func, text, flags=re.DOTALL)

# Add sound to pc_bildirim_goster
sound_logic = '''    def pc_bildirim_goster(self, baslik, mesaj):
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except: pass
        toast = ctk.CTkToplevel(self)'''
        
text = text.replace('''    def pc_bildirim_goster(self, baslik, mesaj):
        toast = ctk.CTkToplevel(self)''', sound_logic)

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
    f.write(text)

print("Update complete")
