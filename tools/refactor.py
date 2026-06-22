import os
import re

replacements = [
    # General terms
    (r'\baktif_siparisler\b', 'active_orders'),
    (r'\bkalemler\b', 'items'),
    (r'\bsiparis_al\b', 'receive_order'),
    (r'\bhesap_kapat\b', 'close_bill'),
    (r'\buzaktan_yazdir\b', 'print_remote'),
    (r'\bfis_yazdir\b', 'print_receipt'),
    (r'\bmenuyu_getir\b', 'get_menu'),
    (r'\bmenuyu_guncelle\b', 'update_menu'),
    (r'\bbaslangic_menu_et\b', 'default_menu_meat'),
    (r'\bbaslangic_menu_tavuk\b', 'default_menu_chicken'),
    (r'\bbaslangic_menu_kampanya\b', 'default_menu_campaign'),
    (r'\bbaslangic_menu_icecekler\b', 'default_menu_drinks'),
    (r'\bbagli_telefonlar\b', 'connected_phones'),
    (r'\bson_kalp_atisi\b', 'last_heartbeat'),
    (r'\bSISTEM_AYARLARI\b', 'SYSTEM_SETTINGS'),
    (r'\bAYAR_DOSYASI\b', 'SETTINGS_FILE'),
    (r'\bfiyat\b', 'price'),
    (r'\bad\b', 'name'),
    (r'\bmusteri_adi\b', 'customer_name'),
    (r'\bmusteriAdi\b', 'customerName'),
    (r'\bsecenekler\b', 'options'),
    (r'\bnotlar\b', 'notes'),
    (r'\btoplam_tutar\b', 'total_amount'),
    (r'\btoplamTutar\b', 'totalAmount'),
    (r'\bdurum\b', 'status'),
    (r'\brenk\b', 'color'),
    (r'\bet\b', 'meat'),
    (r'\btavuk\b', 'chicken'),
    (r'\bkampanya\b', 'campaign'),
    (r'\bicecekler\b', 'drinks'),
    (r'\bekstralar\b', 'extras'),
    (r'\bgramaj\b', 'portion'),
    (r'\bgr\b', 'portion'),
    (r'\bsaat\b', 'time'),
    
    # JSON String Keys specific replacements to ensure strings match correctly
    (r'"musteri_adi"', '"customer_name"'),
    (r'"saat"', '"time"'),
    (r'"kalemler"', '"items"'),
    (r'"toplam_tutar"', '"total_amount"'),
    (r'"ad"', '"name"'),
    (r'"secenekler"', '"options"'),
    (r'"gr"', '"portion"'),
    (r'"fiyat"', '"price"'),
    (r'"notlar"', '"notes"'),
    (r'"durum"', '"status"'),
    (r'"renk"', '"color"'),
    (r'"et"', '"meat"'),
    (r'"tavuk"', '"chicken"'),
    (r'"kampanya"', '"campaign"'),
    (r'"icecekler"', '"drinks"'),
    (r'"ekstralar"', '"extras"'),
    (r'"gramaj"', '"portion"'),
]

root = r'C:\Users\bilal\SARACAPP'

def process_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We do a smart replace:
    new_content = content
    for old, new in replacements:
        new_content = re.sub(old, new, new_content)
        
    if content != new_content:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated: {path}")

# Python files
for f in os.listdir(root):
    if f.endswith('.py') and f.startswith('saracapp_'):
        process_file(os.path.join(root, f))

# Kotlin files
android_root = os.path.join(root, "saracapp2", "app", "src", "main", "java", "com", "bilalgnd", "saracapp")
for dirpath, _, filenames in os.walk(android_root):
    for f in filenames:
        if f.endswith('.kt'):
            process_file(os.path.join(dirpath, f))

print('Refactoring complete.')
