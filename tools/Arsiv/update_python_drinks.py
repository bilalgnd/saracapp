import codecs

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

old_drinks = '''baslangic_menu_icecekler = [
    {"ad": "Kutu Kola", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Sprite", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Fanta", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Şişe Kola", "secenekler": [{"gr": "Standart", "fiyat": 60}]},
    {"ad": "Açık Ayran", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Şalgam", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Ayran", "secenekler": [{"gr": "Standart", "fiyat": 30}]},
    {"ad": "Soda", "secenekler": [{"gr": "Standart", "fiyat": 25}]},
    {"ad": "Su", "secenekler": [{"gr": "Standart", "fiyat": 20}]}
]'''

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

text = text.replace(old_drinks, new_drinks)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Updated kasa_app.pyw drinks list.")
