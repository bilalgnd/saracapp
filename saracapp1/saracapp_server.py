import os
import sys
import json
import time
import logging
import requests
import base64
from urllib.parse import urlencode
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from flask_sock import Sock
import saracapp_models as models
from saracapp_models import SYSTEM_SETTINGS, save_json
from saracapp_config import SETTINGS_FILE
from saracapp_events import ui_event_queue
from saracapp_printer import print_receipt

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    flask_app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    flask_app = Flask(__name__)

CORS(flask_app)

sock = Sock(flask_app)

import threading

connected_phones = set()
ws_lock = threading.Lock()
last_heartbeat = 0

# UI referansini kaldiriyoruz, UI verileri queue uzerinden alacak.
# Ancak baslangic siparislerini gondermek icin bir getter method saglanabilir, 
# ya da state yonetimi models'de tutulabilir. Simdilik UI state guncellemesini takip etmek
# icin global bir active_orders dict'i models'e koyabilirdik, ama basitce WebSocket'ten istek geldiginde UI'a
# guncelleme talebi atalim, ya da UI guncellendiginde burayi cagirsin.
# "telefona_guncelleme_gonder" fonksiyonu saracapp_ui.py'den cagrilacak.

def broadcast_update_to_phones(active_orders):
    data = json.dumps(active_orders)
    with ws_lock:
        with open("ws_debug.log", "a") as f:
            f.write(f"Broadcasting to {len(connected_phones)} sockets. Data: {data[:100]}...\n")
        dead_sockets = []
        for ws in connected_phones:
            try:
                ws.send(data)
            except Exception as e:
                with open("ws_debug.log", "a") as f: f.write(f"Send error: {e}\n")
                dead_sockets.append(ws)
        for ws in dead_sockets:
            connected_phones.remove(ws)

def send_private_message_to_phone(message_dict):
    data = json.dumps(message_dict)
    with ws_lock:
        dead_sockets = []
        for ws in connected_phones:
            try:
                ws.send(data)
            except Exception:
                dead_sockets.append(ws)
        for ws in dead_sockets:
            connected_phones.remove(ws)

@flask_app.route('/')
def home_page():
    return render_template('index.html')

@flask_app.route('/tv')
def tv_page():
    return render_template('tv.html')

@flask_app.route('/tv_settings')
def tv_settings():
    return jsonify({"youtube_url": SYSTEM_SETTINGS.get("YOUTUBE_LINK", "")})

@sock.route('/ws')
def websocket_connection_handler(ws):
    with ws_lock:
        connected_phones.add(ws)
    ui_event_queue.put({"action": "request_update"})
    try:
        while True:
            message = ws.receive()
            global last_heartbeat
            last_heartbeat = time.time()
    except Exception as e:
        logger.warning(f"WebSocket baglantisi koptu: {e}")
        with ws_lock:
            if ws in connected_phones:
                connected_phones.remove(ws)

@flask_app.route('/siparis', methods=['POST'])
def receive_order():
    data = request.get_json()
    ui_event_queue.put({"action": "order_received", "data": data})
    return jsonify({"status": "basarili"})

@flask_app.route('/debug_html', methods=['POST'])
def receive_debug_html():
    data = request.get_json()
    platform = data.get("platform", "Unknown")
    html_content = data.get("html", "")
    with open(f"debug_{platform}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    return jsonify({"status": "ok"})

@flask_app.route('/close_bill', methods=['POST'])
def close_bill():
    data = request.get_json()
    ui_event_queue.put({"action": "order_deleted", "data": data["customer_name"]})
    return jsonify({"success": True})

@flask_app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    ui_event_queue.put({"action": "update_status", "data": data})
    return jsonify({"success": True})

@flask_app.route('/yazdir', methods=['POST'])
def print_remote():
    try:
        m_adi = request.get_json()["customer_name"]
        ui_event_queue.put({"action": "print_receipt", "data": {"customer_name": m_adi}})
        return jsonify({"status": "basarili"})
    except Exception as e:
        return jsonify({"status": "hata", "error": str(e)}), 400

@flask_app.route('/test_orders', methods=['GET'])
def test_orders():
    return jsonify({"orders": [a["customer_name"] for a in models.active_orders]})

@flask_app.route('/menu', methods=['GET'])
def get_menu():
    from saracapp_models import default_menu_meat, default_menu_chicken, default_menu_campaign, default_menu_drinks
    from saracapp_config import PAID_EXTRAS
    
    def get_current_price(product_name, portion, ori_fiyat):
        return models.PRICE_MEMORY.get(f"{product_name}_{portion}", ori_fiyat)
    
    def update_menu(ori_menu):
        return [{"name": u["name"], "options": [{"portion": s["portion"], "price": get_current_price(u["name"], s["portion"], s["price"])} for s in u["options"]]} for u in ori_menu]

    return jsonify({
        "meat": update_menu(default_menu_meat),
        "chicken": update_menu(default_menu_chicken),
        "campaign": update_menu(default_menu_campaign),
        "drinks": update_menu(default_menu_drinks),
        "extras": PAID_EXTRAS
    })

@flask_app.route('/spotify/login')
def spotify_login():
    SPOTIFY_CLIENT_ID = SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_ID", "")
    if not SPOTIFY_CLIENT_ID:
        return "Lutfen once Kasa ayarlarindan Client ID girin."
    scope = "streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state"
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "response_type": "code",
        "client_id": SPOTIFY_CLIENT_ID,
        "scope": scope,
        "redirect_uri": "http://127.0.0.1:5000/spotify/callback"
    })
    return redirect(auth_url)

@flask_app.route('/spotify/callback')
def spotify_callback():
    code = request.args.get('code')
    if not code:
        return "Spotify baglantisi reddedildi."
    
    SPOTIFY_CLIENT_ID = SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_SECRET", "")
    
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:5000/spotify/callback"
    }, headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    
    if res.status_code == 200:
        data = res.json()
        SYSTEM_SETTINGS["SPOTIFY_ACCESS_TOKEN"] = data.get("access_token")
        SYSTEM_SETTINGS["SPOTIFY_REFRESH_TOKEN"] = data.get("refresh_token")
        save_json(SETTINGS_FILE, SYSTEM_SETTINGS)
        return "Spotify basariyla baglandi! Kasa uygulamasina donebilirsiniz. Bu pencereyi kapatabilirsiniz."
    else:
        return f"Hata: {res.text}"

@flask_app.route('/spotify/token')
def spotify_token():
    access_token = SYSTEM_SETTINGS.get("SPOTIFY_ACCESS_TOKEN", "")
    refresh_token = SYSTEM_SETTINGS.get("SPOTIFY_REFRESH_TOKEN", "")
    if not access_token or not refresh_token:
        return jsonify({"error": "not_logged_in"}), 401
        
    test_res = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"})
    if test_res.status_code == 401:
        SPOTIFY_CLIENT_ID = SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_ID", "")
        SPOTIFY_CLIENT_SECRET = SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_SECRET", "")
        auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        ref_res = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }, headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        if ref_res.status_code == 200:
            data = ref_res.json()
            SYSTEM_SETTINGS["SPOTIFY_ACCESS_TOKEN"] = data.get("access_token")
            if "refresh_token" in data:
                SYSTEM_SETTINGS["SPOTIFY_REFRESH_TOKEN"] = data.get("refresh_token")
            save_json(SETTINGS_FILE, SYSTEM_SETTINGS)
            access_token = SYSTEM_SETTINGS["SPOTIFY_ACCESS_TOKEN"]
        else:
            return jsonify({"error": "refresh_failed"}), 401
            
    return jsonify({"access_token": access_token})

def run_server(host, port):
    # Flask output'u kapatmak isterseniz logging konfigure edilebilir
    flask_app.run(host=host, port=port, debug=False, use_reloader=False)
