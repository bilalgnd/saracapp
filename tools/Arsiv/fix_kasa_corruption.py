import codecs

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    lines = f.readlines()

new_drinks_str = """baslangic_menu_icecekler = [
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
]
"""

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("baslangic_menu_icecekler = ["):
        start_idx = i
    if start_idx != -1 and line.startswith("UCRETLI_EKSTRALAR ="):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    del lines[start_idx:end_idx]
    lines.insert(start_idx, new_drinks_str)
    
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.writelines(lines)
    print("Fixed corrupted drinks array successfully.")
else:
    print(f"Could not find bounds: {start_idx}, {end_idx}")

