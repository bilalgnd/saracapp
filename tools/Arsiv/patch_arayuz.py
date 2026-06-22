import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    content = f.read()

old_code = '''                    def arayuz_sor():
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
                                
                            ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=5, padx=20, fill="x")'''

new_code = '''                    def arayuz_sor():
                        panel = ctk.CTkToplevel(self)
                        panel.title("Guncelleme Yoneticisi")
                        w, h = 450, 400
                        x = (self.winfo_screenwidth() - w) // 2
                        y = (self.winfo_screenheight() - h) // 2
                        panel.geometry(f"{w}x{h}+{x}+{y}")
                        panel.attributes("-topmost", True)
                        panel.grab_set()
                        
                        def exe_indir():
                            import webbrowser
                            if exe_url: webbrowser.open(exe_url)
                        
                        def mobile_yolla():
                            if apk_url:
                                try: telefona_ozel_mesaj_gonder({"type": "apk_guncelleme", "url": apk_url})
                                except: pass
                                durum_lbl.configure(text="Garsonlara bildirim basariyla yollandi!", text_color="#FFEB3B")
                        
                        if tag == "v4.0.1" or tag == "4.0.1":
                            ctk.CTkLabel(panel, text=f"Kasa Uygulamasi Guncel ({tag})", font=("Arial", 22, "bold"), text_color="#2196F3").pack(pady=15)
                            ctk.CTkLabel(panel, text="Ancak garson tabletleri guncel degilse\\nasagidan onlara guncelleme gonderebilirsiniz.", font=("Arial", 14)).pack(pady=5)
                            if apk_url:
                                ctk.CTkButton(panel, text="Garsonlara (Tablet) Guncelleme Gonder", font=("Arial", 16, "bold"), fg_color="#F44336", hover_color="#D32F2F", command=mobile_yolla, height=45).pack(pady=15, padx=20, fill="x")
                            
                            durum_lbl = ctk.CTkLabel(panel, text="", font=("Arial", 15, "bold"))
                            durum_lbl.pack(pady=5)
                            ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=10, padx=20, fill="x")
                        else:
                            if not apk_url and not exe_url:
                                ctk.CTkLabel(panel, text=f"Versiyon Guncel", font=("Arial", 22, "bold"), text_color="#2196F3").pack(pady=20)
                                ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=15, padx=20, fill="x")
                                return
                                
                            ctk.CTkLabel(panel, text=f"Yeni Versiyon Bulundu: {tag}", font=("Arial", 22, "bold"), text_color="#4CAF50").pack(pady=20)
                            
                            if exe_url:
                                ctk.CTkButton(panel, text="PC Exe Indir (Tarayicida)", font=("Arial", 16, "bold"), command=exe_indir, height=45).pack(pady=10, padx=20, fill="x")
                            if apk_url:
                                ctk.CTkButton(panel, text="Garsonlara APK Gonder", font=("Arial", 16, "bold"), fg_color="#F44336", hover_color="#D32F2F", command=mobile_yolla, height=45).pack(pady=10, padx=20, fill="x")
                            
                            durum_lbl = ctk.CTkLabel(panel, text="", font=("Arial", 15, "bold"))
                            durum_lbl.pack(pady=5)
                                
                            ctk.CTkButton(panel, text="Kapat", font=("Arial", 16), fg_color="#424242", hover_color="#616161", command=panel.destroy, height=40).pack(pady=5, padx=20, fill="x")'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Could not find old code.")
