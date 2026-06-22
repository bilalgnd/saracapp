import json
import os
import threading
import logging
import traceback
from saracapp_config import PRICES_FILE, SETTINGS_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json(path, default_val):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as d:
                return json.load(d)
        except Exception as e:
            logger.error(f"Error loading JSON from {path}: {e}\n{traceback.format_exc()}")
            return default_val
    return default_val

file_lock = threading.Lock()

def _save_json_thread(path, data):
    try:
        with file_lock:
            with open(path, "w", encoding="utf-8") as d:
                json.dump(data, d, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}\n{traceback.format_exc()}")

def save_json(path, data):
    import copy
    data_copy = copy.deepcopy(data)
    # Asynchronous save
    threading.Thread(target=_save_json_thread, args=(path, data_copy), daemon=True).start()

PRICE_MEMORY = load_json(PRICES_FILE, {})
SYSTEM_SETTINGS = load_json(SETTINGS_FILE, {"YAZICI_ADI": ""})

# SINGLE SOURCE OF TRUTH FOR ORDERS
from saracapp_config import TABLES_FILE
active_orders = load_json(TABLES_FILE, [])

def get_current_price(product_name, portion, ori_fiyat):
    return PRICE_MEMORY.get(f"{product_name}_{portion}", ori_fiyat)

def update_menu(ori_menu):
    return [
        {
            "name": u["name"],
            "options": [
                {
                    "portion": s["portion"],
                    "price": get_current_price(u["name"], s["portion"], s["price"])
                } for s in u["options"]
            ]
        } for u in ori_menu
    ]

# MENULER
default_menu_meat = [
    {"name": "Et Tombik", "options": [{"portion": "50gr", "price": 250}, {"portion": "100gr", "price": 350}, {"portion": "150gr", "price": 450}]},
    {"name": "Et Durum", "options": [{"portion": "50gr", "price": 250}, {"portion": "100gr", "price": 350}, {"portion": "150gr", "price": 450}]},
    {"name": "Et XL Durum", "options": [{"portion": "120gr", "price": 400}, {"portion": "170gr", "price": 500}, {"portion": "220gr", "price": 600}]},
    {"name": "Et Eski Usul", "options": [{"portion": "50gr", "price": 250}, {"portion": "100gr", "price": 350}, {"portion": "150gr", "price": 450}]},
    {"name": "Et Porsiyon", "options": [{"portion": "120gr", "price": 500}, {"portion": "170gr", "price": 600}, {"portion": "220gr", "price": 700}]},
    {"name": "Et Pilav Ustu", "options": [{"portion": "120gr", "price": 550}, {"portion": "170gr", "price": 650}, {"portion": "220gr", "price": 750}]},
    {"name": "Beyti", "options": [{"portion": "100gr", "price": 650}, {"portion": "150gr", "price": 750}, {"portion": "200gr", "price": 850}]},
    {"name": "Iskender", "options": [{"portion": "100gr", "price": 650}, {"portion": "150gr", "price": 750}, {"portion": "200gr", "price": 850}]}
]
default_menu_chicken = [
    {"name": "Tavuk Tombik", "options": [{"portion": "100gr", "price": 140}, {"portion": "150gr", "price": 200}, {"portion": "200gr", "price": 250}]},
    {"name": "Tavuk Durum", "options": [{"portion": "100gr", "price": 140}, {"portion": "150gr", "price": 200}, {"portion": "200gr", "price": 250}]},
    {"name": "Tavuk XL Durum", "options": [{"portion": "120gr", "price": 170}, {"portion": "170gr", "price": 220}, {"portion": "220gr", "price": 270}]},
    {"name": "Hatay Usulu", "options": [{"portion": "100gr", "price": 170}, {"portion": "150gr", "price": 220}, {"portion": "200gr", "price": 270}]},
    {"name": "Tavuk Eski Usul", "options": [{"portion": "100gr", "price": 140}, {"portion": "150gr", "price": 200}, {"portion": "200gr", "price": 250}]},
    {"name": "Biga Doneri", "options": [{"portion": "100gr", "price": 120}]},
    {"name": "Tavuk Porsiyon", "options": [{"portion": "100gr", "price": 250}, {"portion": "150gr", "price": 300}, {"portion": "200gr", "price": 350}]},
    {"name": "Tavuk Pilav Ustu", "options": [{"portion": "100gr", "price": 300}, {"portion": "150gr", "price": 350}, {"portion": "200gr", "price": 400}]}
]
default_menu_campaign = [
    {"name": "Tavuk Kampy", "options": [{"portion": "Standart", "price": 120}]},
    {"name": "Et Kampy", "options": [{"portion": "Standart", "price": 220}]},
    {"name": "500gr Et", "options": [{"portion": "Standart", "price": 1250}]},
    {"name": "500gr Tavuk", "options": [{"portion": "Standart", "price": 600}]}
]
default_menu_drinks = [
    {"name": "Kutu Kola", "options": [{"portion": "Standart", "price": 80}]},
    {"name": "Ayran", "options": [{"portion": "Standart", "price": 30}]},
    {"name": "Acik Ayran", "options": [{"portion": "Standart", "price": 50}]},
    {"name": "Sise Kola", "options": [{"portion": "Standart", "price": 60}]},
    {"name": "Su", "options": [{"portion": "Standart", "price": 20}]},
    {"name": "Sprite", "options": [{"portion": "Standart", "price": 80}]},
    {"name": "Fanta", "options": [{"portion": "Standart", "price": 80}]},
    {"name": "Cola Zero", "options": [{"portion": "Standart", "price": 80}]},
    {"name": "Salgam", "options": [{"portion": "Standart", "price": 50}]},
    {"name": "Soda", "options": [{"portion": "Standart", "price": 25}]}
]
