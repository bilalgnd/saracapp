import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'def yazici_ayari_penceresi(self):' in line:
        start_idx = i
        break

if start_idx != -1:
    for i in range(start_idx + 1, len(lines)):
        if 'def masalari_diske_kaydet_ve_yay(self):' in lines[i]:
            end_idx = i - 1
            break

new_func = '''    def yazici_ayari_penceresi(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Yazici Secimi")
        popup.geometry("500x300")
        popup.attributes("-topmost", True)
        popup.grab_set()
        
        ctk.CTkLabel(popup, text="Windows Yazici Secin", font=("Arial", 20, "bold")).pack(pady=20)
        
        try:
            import win32print
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        except Exception:
            printers = []
            
        if not printers: printers = ["Yazici Bulunamadi"]

        secili_yazici = ctk.StringVar(value=SISTEM_AYARLARI.get("YAZICI_ADI", printers[0] if printers else ""))
        
        yazici_menu = ctk.CTkOptionMenu(popup, values=printers, variable=secili_yazici, font=("Arial", 18), width=400, height=50)
        yazici_menu.pack(pady=10)
        
        def kaydet(): 
            val = secili_yazici.get().strip()
            if val and val != "Yazici Bulunamadi":
                SISTEM_AYARLARI["YAZICI_ADI"] = val
                json_kaydet(AYAR_DOSYASI, SISTEM_AYARLARI)
                messagebox.showinfo("Basarili", "Yazici Kaydedildi!")
            popup.destroy()
            
        ctk.CTkButton(popup, text="Kaydet", fg_color="#4CAF50", font=("Arial", 18, "bold"), height=50, command=kaydet).pack(pady=20)

'''

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
    f.writelines(lines[:start_idx])
    f.write(new_func)
    f.writelines(lines[end_idx+1:])
print('Replace complete.')
