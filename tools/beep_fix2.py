import codecs

with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'r', 'utf-8') as f:
    content = f.read()

old_func = '''winsound.MessageBeep(winsound.MB_ICONASTERISK)'''
new_func = '''import threading\n            threading.Thread(target=lambda: winsound.Beep(1000, 300), daemon=True).start()'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with codecs.open('C:/Users/bilal/SARACAPP/kasa_app.pyw', 'w', 'utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Not found")
