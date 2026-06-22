import codecs
import re

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

pattern = r'baslangic_menu_icecekler = \[\s+{"ad": "Kutu Kola".*?\]'

new_drinks = '''baslangic_menu_icecekler = [
    {"ad": "Kutu Kola", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Ayran", "secenekler": [{"gr": "Standart", "fiyat": 30}]},
    {"ad": "Açık Ayran", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Şişe Kola", "secenekler": [{"gr": "Standart", "fiyat": 60}]},
    {"ad": "Su", "secenekler": [{"gr": "Standart", "fiyat": 20}]},
    {"ad": "Sprite", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Fanta", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Cola Zero", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Şalgam", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Soda", "secenekler": [{"gr": "Standart", "fiyat": 25}]}
]'''

if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, new_drinks, text, flags=re.DOTALL)
    print("Replaced drinks list using regex.")
else:
    print("Could not find the drinks list pattern.")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
