import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'self.after(0, arayuz_sor)' in line:
        new_lines.append('                else:\n')
        new_lines.append('                    err_msg = "GitHub API baglanti hatasi (Kod: " + str(response.status_code) + ")"\n')
        new_lines.append('                    self.after(0, lambda msg=err_msg: messagebox.showerror("Hata", msg))\n')

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
    f.writelines(new_lines)
print("Added else branch.")
