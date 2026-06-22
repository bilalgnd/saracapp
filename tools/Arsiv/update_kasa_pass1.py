import codecs
import re

filepath = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Replace menus with Pure ASCII
menus = '''baslangic_menu_et = [
    {"ad": "Et Tombik", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et Durum", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et XL Durum", "secenekler": [{"gr": "120gr", "fiyat": 400}, {"gr": "170gr", "fiyat": 500}, {"gr": "220gr", "fiyat": 600}]},
    {"ad": "Et Eski Usul", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et Porsiyon", "secenekler": [{"gr": "120gr", "fiyat": 500}, {"gr": "170gr", "fiyat": 600}, {"gr": "220gr", "fiyat": 700}]},
    {"ad": "Et Pilav Ustu", "secenekler": [{"gr": "120gr", "fiyat": 550}, {"gr": "170gr", "fiyat": 650}, {"gr": "220gr", "fiyat": 750}]},
    {"ad": "Beyti", "secenekler": [{"gr": "100gr", "fiyat": 650}, {"gr": "150gr", "fiyat": 750}, {"gr": "200gr", "fiyat": 850}]},
    {"ad": "Iskender", "secenekler": [{"gr": "100gr", "fiyat": 650}, {"gr": "150gr", "fiyat": 750}, {"gr": "200gr", "fiyat": 850}]}
]
baslangic_menu_tavuk = [
    {"ad": "Tavuk Tombik", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Tavuk Durum", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Tavuk XL Durum", "secenekler": [{"gr": "120gr", "fiyat": 170}, {"gr": "170gr", "fiyat": 220}, {"gr": "220gr", "fiyat": 270}]},
    {"ad": "Hatay Usulu", "secenekler": [{"gr": "100gr", "fiyat": 170}, {"gr": "150gr", "fiyat": 220}, {"gr": "200gr", "fiyat": 270}]},
    {"ad": "Tavuk Eski Usul", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Biga Doneri", "secenekler": [{"gr": "100gr", "fiyat": 120}]},
    {"ad": "Tavuk Porsiyon", "secenekler": [{"gr": "100gr", "fiyat": 250}, {"gr": "150gr", "fiyat": 300}, {"gr": "200gr", "fiyat": 350}]},
    {"ad": "Tavuk Pilav Ustu", "secenekler": [{"gr": "100gr", "fiyat": 300}, {"gr": "150gr", "fiyat": 350}, {"gr": "200gr", "fiyat": 400}]}
]
baslangic_menu_kampanya = [
    {"ad": "Tavuk Doner + Ayran", "secenekler": [{"gr": "Standart", "fiyat": 120}]},
    {"ad": "Et Doner + Ayran", "secenekler": [{"gr": "Standart", "fiyat": 220}]},
    {"ad": "500gr Et", "secenekler": [{"gr": "Standart", "fiyat": 1250}]},
    {"ad": "500gr Tavuk", "secenekler": [{"gr": "Standart", "fiyat": 600}]}
]
baslangic_menu_icecekler = [
    {"ad": "Kutu Kola", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Ayran", "secenekler": [{"gr": "Standart", "fiyat": 30}]},
    {"ad": "Acik Ayran", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Sise Kola", "secenekler": [{"gr": "Standart", "fiyat": 60}]},
    {"ad": "Su", "secenekler": [{"gr": "Standart", "fiyat": 20}]},
    {"ad": "Sprite", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Fanta", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Cola Zero", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Salgam", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Soda", "secenekler": [{"gr": "Standart", "fiyat": 25}]}
]
UCRETLI_EKSTRALAR = {"Cheddar": 70, "Kasarli": 70}'''

# Extract the region to replace (from baslangic_menu_et to UCRETLI_EKSTRALAR = ...)
start_idx = text.find('baslangic_menu_et = [')
end_idx = text.find('UCRETLI_EKSTRALAR = ', start_idx)
end_idx = text.find('\n', end_idx) + 1

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + menus + "\n" + text[end_idx:]


# Replace the Window Title
text = re.sub(r'self\.title\("saracapp"\)', 'self.title("SARACOGLU DONER v4.0.5")', text)

# Replace the product colors section (finding by start and end lines)
colors_start = text.find("ad_kucuk = urun['ad'].lower()")
colors_end = text.find("buton_yazisi = f\"{urun['ad']}", colors_start)

new_colors = '''            ad_kucuk = urun['ad'].lower()
            if "tombik" in ad_kucuk: bg_renk = "#FF9800"; txt_renk = "black"; hov_renk = "#F57C00"
            elif "eski usul" in ad_kucuk: bg_renk = "#F44336"; txt_renk = "white"; hov_renk = "#D32F2F"
            elif "durum" in ad_kucuk: bg_renk = "#FFEB3B"; txt_renk = "black"; hov_renk = "#FBC02D"
            elif any(x in ad_kucuk for x in ["et porsiyon", "beyti", "iskender"]) or ("pilav ustu" in ad_kucuk and "tavuk" not in ad_kucuk): bg_renk = "#8B0000"; txt_renk = "white"; hov_renk = "#B71C1C"
            elif "hatay" in ad_kucuk: bg_renk = "#F5DEB3"; txt_renk = "black"; hov_renk = "#D2B48C"
            elif "biga" in ad_kucuk: bg_renk = "#1976D2"; txt_renk = "white"; hov_renk = "#1565C0"
            elif "tavuk porsiyon" in ad_kucuk or ("pilav ustu" in ad_kucuk and "tavuk" in ad_kucuk): bg_renk = "#FFFF5722"; txt_renk = "black"; hov_renk = "#E64A19"
            elif any(x in ad_kucuk for x in ["kola", "ayran", "su", "soda", "sprite", "fanta", "salgam", "zero"]): bg_renk = "#0277BD"; txt_renk = "white"; hov_renk = "#01579B"
            else: bg_renk = "#37474F" if self.ayarlar_modu else "#1E1E1E"; txt_renk = "white"; hov_renk = "#455A64" if self.ayarlar_modu else "#333333"
            
            '''

if colors_start != -1 and colors_end != -1:
    text = text[:colors_start] + new_colors + text[colors_end:]

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)

print("Pass 1: Menus and basic colors updated.")
