import os

APPDATA_DIR = os.path.join(os.getenv('APPDATA', ''), 'SaracogluDoner')
os.makedirs(APPDATA_DIR, exist_ok=True)
PRICES_FILE = os.path.join(APPDATA_DIR, "saracoglu_fiyatlar.json")
SETTINGS_FILE = os.path.join(APPDATA_DIR, "saracoglu_ayarlar.json")
TABLES_FILE = os.path.join(APPDATA_DIR, "aktif_masalar.json")

CASH_REGISTER_IP = "127.0.0.1"
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    CASH_REGISTER_IP = s.getsockname()[0]
    s.close()
except Exception:
    pass

ACTIVE_PORT = 5000

PAID_EXTRAS = {"Cheddar": 70, "Kasarli": 70}
