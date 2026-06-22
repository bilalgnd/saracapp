import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def pc_bildirim_goster(self, baslik, mesaj):' in line:
        # Insert the beep code right after this line
        beep_code = "        try:\n            import winsound, threading\n            threading.Thread(target=lambda: winsound.Beep(1000, 300), daemon=True).start()\n        except: pass\n"
        lines.insert(i + 1, beep_code)
        break

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
    f.writelines(lines)

print("Beep added.")
