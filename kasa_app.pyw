import customtkinter as ctk
import json
import os
import tkinter.messagebox as messagebox
import threading
import time
import socket
import datetime
import keyboard
import requests
import sys
import webbrowser
from flask import Flask, request, jsonify, render_template
from flask_sock import Sock



try:
    import setproctitle
    setproctitle.setproctitle("notepad")
except ImportError: pass

try:
    import win32print
    YAZICI_AKTIF = True
except ImportError:
    YAZICI_AKTIF = False

APPDATA_DIR = os.path.join(os.getenv('APPDATA', ''), 'SaracogluDoner')
os.makedirs(APPDATA_DIR, exist_ok=True)
VERI_DOSYASI = os.path.join(APPDATA_DIR, "saracoglu_fiyatlar.json")
AYAR_DOSYASI = os.path.join(APPDATA_DIR, "saracoglu_ayarlar.json")
MASALAR_DOSYASI = os.path.join(APPDATA_DIR, "aktif_masalar.json")

def json_yukle(yol, varsayilan):
    if os.path.exists(yol):
        try:
            with open(yol, "r", encoding="utf-8") as d: return json.load(d)
        except: return varsayilan
    return varsayilan

def json_kaydet(yol, veri):
    with open(yol, "w", encoding="utf-8") as d: json.dump(veri, d, ensure_ascii=False, indent=4)

FIYAT_HAFIZASI = json_yukle(VERI_DOSYASI, {})
SISTEM_AYARLARI = json_yukle(AYAR_DOSYASI, {"YAZICI_ADI": ""})

def guncel_fiyat(urun_adi, gramaj, ori_fiyat): return FIYAT_HAFIZASI.get(f"{urun_adi}_{gramaj}", ori_fiyat)
def menuyu_guncelle(ori_menu): return [{"ad": u["ad"], "secenekler": [{"gr": s["gr"], "fiyat": guncel_fiyat(u["ad"], s["gr"], s["fiyat"])} for s in u["secenekler"]]} for u in ori_menu]

def yerel_ip_bul():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('10.255.255.255', 1)); IP = s.getsockname()[0]
    except Exception: IP = '127.0.0.1'
    finally: s.close()
    return IP

KASA_IP = yerel_ip_bul()

baslangic_menu_et = [
    {"ad": "Et Tombik", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et Dürüm", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et XL Dürüm", "secenekler": [{"gr": "120gr", "fiyat": 400}, {"gr": "170gr", "fiyat": 500}, {"gr": "220gr", "fiyat": 600}]},
    {"ad": "Et Eski Usul", "secenekler": [{"gr": "50gr", "fiyat": 250}, {"gr": "100gr", "fiyat": 350}, {"gr": "150gr", "fiyat": 450}]},
    {"ad": "Et Porsiyon", "secenekler": [{"gr": "120gr", "fiyat": 500}, {"gr": "170gr", "fiyat": 600}, {"gr": "220gr", "fiyat": 700}]},
    {"ad": "Et Pilav Üstü", "secenekler": [{"gr": "120gr", "fiyat": 550}, {"gr": "170gr", "fiyat": 650}, {"gr": "220gr", "fiyat": 750}]},
    {"ad": "Beyti", "secenekler": [{"gr": "100gr", "fiyat": 650}, {"gr": "150gr", "fiyat": 750}, {"gr": "200gr", "fiyat": 850}]},
    {"ad": "İskender", "secenekler": [{"gr": "100gr", "fiyat": 650}, {"gr": "150gr", "fiyat": 750}, {"gr": "200gr", "fiyat": 850}]}
]
baslangic_menu_tavuk = [
    {"ad": "Tavuk Tombik", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Tavuk Dürüm", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Tavuk XL Dürüm", "secenekler": [{"gr": "120gr", "fiyat": 170}, {"gr": "170gr", "fiyat": 220}, {"gr": "220gr", "fiyat": 270}]},
    {"ad": "Hatay Usulü", "secenekler": [{"gr": "100gr", "fiyat": 170}, {"gr": "150gr", "fiyat": 220}, {"gr": "200gr", "fiyat": 270}]},
    {"ad": "Tavuk Eski Usul", "secenekler": [{"gr": "100gr", "fiyat": 140}, {"gr": "150gr", "fiyat": 200}, {"gr": "200gr", "fiyat": 250}]},
    {"ad": "Biga Döneri", "secenekler": [{"gr": "100gr", "fiyat": 120}]},
    {"ad": "Tavuk Porsiyon", "secenekler": [{"gr": "100gr", "fiyat": 250}, {"gr": "150gr", "fiyat": 300}, {"gr": "200gr", "fiyat": 350}]},
    {"ad": "Tavuk Pilav Üstü", "secenekler": [{"gr": "100gr", "fiyat": 300}, {"gr": "150gr", "fiyat": 350}, {"gr": "200gr", "fiyat": 400}]}
]
baslangic_menu_kampanya = [
    {"ad": "Tavuk Döner + Ayran", "secenekler": [{"gr": "Standart", "fiyat": 120}]},
    {"ad": "Et Döner + Ayran", "secenekler": [{"gr": "Standart", "fiyat": 220}]},
    {"ad": "500gr Et", "secenekler": [{"gr": "Standart", "fiyat": 1250}]},
    {"ad": "500gr Tavuk", "secenekler": [{"gr": "Standart", "fiyat": 600}]}
]
baslangic_menu_icecekler = [
    {"ad": "Kutu Kola", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Sprite", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Fanta", "secenekler": [{"gr": "Standart", "fiyat": 80}]},
    {"ad": "Şişe Kola", "secenekler": [{"gr": "Standart", "fiyat": 60}]},
    {"ad": "Açık Ayran", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Şalgam", "secenekler": [{"gr": "Standart", "fiyat": 50}]},
    {"ad": "Ayran", "secenekler": [{"gr": "Standart", "fiyat": 30}]},
    {"ad": "Soda", "secenekler": [{"gr": "Standart", "fiyat": 25}]},
    {"ad": "Su", "secenekler": [{"gr": "Standart", "fiyat": 20}]}
]
UCRETLI_EKSTRALAR = {"Cheddar": 70, "Kaşarlı": 70}

def usb_fis_yazdir(musteri_adi, kalemler, toplam_tutar, saat=""):
    if not YAZICI_AKTIF: return
    yazici_adi = SISTEM_AYARLARI.get("YAZICI_ADI", "")
    if not yazici_adi: return
    def temizle(m): return m.replace("ı","i").replace("İ","I").replace("ğ","g").replace("Ğ","G").replace("ü","u").replace("Ü","U").replace("ş","s").replace("Ş","S").replace("ö","o").replace("Ö","O").replace("ç","c").replace("Ç","C")
    ESC_INIT = b'\x1B\x40'; ALIGN_LEFT = b'\x1B\x61\x00'; ALIGN_CENTER = b'\x1B\x61\x01'  
    BOLD_ON = b'\x1B\x45\x01'; BOLD_OFF = b'\x1B\x45\x00'; SIZE_NORMAL = b'\x1D\x21\x00'; SIZE_UZUN = b'\x1D\x21\x01'; SIZE_DEV = b'\x1D\x21\x11'; CUT = b'\x1D\x56\x41\x00'       
    
    def satir_hizala(sol_m, sag_m, t_karakter=42):
        bos = t_karakter - len(sol_m) - len(sag_m)
        return f"{sol_m}{' ' * bos}{sag_m}" if bos > 0 else f"{sol_m} {sag_m}"

    fis = bytearray()
    fis += ESC_INIT + ALIGN_CENTER + SIZE_DEV + BOLD_ON + b"SARACOGLU DONER\n" + SIZE_NORMAL + BOLD_OFF + b"\n"
    fis += SIZE_UZUN + BOLD_ON + f"Masa: {temizle(musteri_adi)}\n".encode("ascii", errors="replace") + SIZE_NORMAL + BOLD_OFF
    fis += f"Saat: {saat if saat else datetime.datetime.now().strftime('%H:%M')}\n".encode("ascii", errors="replace") + b"------------------------------------------\n" + ALIGN_LEFT
    
    gruplu = {}
    for k in kalemler:
        anh = f"{k['ad']}_{k['gramaj']}_{k['notlar']}"
        if anh not in gruplu: gruplu[anh] = []
        gruplu[anh].append(k)

    for _, ls in gruplu.items():
        ilk = ls[0]; adet = len(ls); gr = f" {ilk['gramaj']}" if ilk['gramaj'] != "Standart" else ""
        fis += SIZE_UZUN + BOLD_ON + (satir_hizala(f"{adet}x {temizle(ilk['ad'])}{gr}", f"{ilk['fiyat'] * adet},00") + "\n").encode("ascii", errors="replace")
        if ilk.get('notlar'): fis += SIZE_NORMAL + BOLD_OFF + f"   * {temizle(ilk['notlar'])}\n".encode("ascii", errors="replace")

    fis += ALIGN_CENTER + SIZE_NORMAL + BOLD_OFF + b"------------------------------------------\n"
    fis += SIZE_DEV + BOLD_ON + f"GENEL TOPLAM:  {toplam_tutar},00\n".encode("ascii", errors="replace")
    fis += SIZE_NORMAL + BOLD_OFF + b"------------------------------------------\nAFIYET OLSUN\n\n\n\n\n\n"

    try:
        hPrinter = win32print.OpenPrinter(yazici_adi)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Adisyon", None, "RAW"))
            win32print.StartPagePrinter(hPrinter); win32print.WritePrinter(hPrinter, bytes(fis)); win32print.WritePrinter(hPrinter, CUT)
            win32print.EndPagePrinter(hPrinter); win32print.EndDocPrinter(hPrinter)
        finally: win32print.ClosePrinter(hPrinter)
    except Exception: pass

import sys
import os
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    flask_app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    flask_app = Flask(__name__)
sock = Sock(flask_app)

@flask_app.route('/')
def ana_sayfa():
    return render_template('index.html')
kasa_arayuz_referansi = None 
bagli_telefonlar = set()
son_kalp_atisi = 0

def telefona_guncelleme_gonder():
    if kasa_arayuz_referansi:
        veri = json.dumps(kasa_arayuz_referansi.aktif_siparisler)
        for ws in list(bagli_telefonlar):
            try: ws.send(veri)
            except: bagli_telefonlar.remove(ws)

def telefona_ozel_mesaj_gonder(mesaj_dict):
    veri = json.dumps(mesaj_dict)
    for ws in list(bagli_telefonlar):
        try: ws.send(veri)
        except: bagli_telefonlar.remove(ws)

@sock.route('/ws')
def websocket_baglantisi(ws):
    bagli_telefonlar.add(ws)
    try:
        if kasa_arayuz_referansi: ws.send(json.dumps(kasa_arayuz_referansi.aktif_siparisler))
        while True:
            mesaj = ws.receive()
            global son_kalp_atisi; son_kalp_atisi = time.time()
    except:
        if ws in bagli_telefonlar: bagli_telefonlar.remove(ws)

@flask_app.route('/siparis', methods=['POST'])
def siparis_al():
    veri = request.get_json(); kasa_arayuz_referansi.telefondan_siparis_geldi(veri); return jsonify({"status": "basarili"})

@flask_app.route('/hesap_kapat', methods=['POST'])
def hesap_kapat():
    veri = request.get_json(); kasa_arayuz_referansi.telefondan_silme_geldi(veri["musteri_adi"]); return jsonify({"status": "basarili"})

@flask_app.route('/yazdir', methods=['POST'])
def uzaktan_yazdir():
    try:
        m_adi = request.get_json()["musteri_adi"]
        for a in kasa_arayuz_referansi.aktif_siparisler:
            if a["musteri_adi"] == m_adi:
                usb_fis_yazdir(m_adi, a["kalemler"], a["toplam_tutar"], a.get('saat', ''))
                return jsonify({"status": "basarili"})
        return jsonify({"status": "hata"}), 404
    except Exception: return jsonify({"status": "hata"}), 400

@flask_app.route('/menu', methods=['GET'])
def menuyu_getir():
    guncel_et = menuyu_guncelle(baslangic_menu_et)
    guncel_tavuk = menuyu_guncelle(baslangic_menu_tavuk)
    guncel_kampanya = menuyu_guncelle(baslangic_menu_kampanya)
    guncel_icecekler = menuyu_guncelle(baslangic_menu_icecekler)
    
    return jsonify({
        "et": guncel_et,
        "tavuk": guncel_tavuk,
        "kampanya": guncel_kampanya,
        "icecekler": guncel_icecekler,
        "ekstralar": UCRETLI_EKSTRALAR
    })

def port_musait_mi(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

AKTIF_PORT = 5000
for p in range(5000, 5010):
    if port_musait_mi(p):
        AKTIF_PORT = p
        break

def sunucuyu_baslat(): flask_app.run(host='0.0.0.0', port=AKTIF_PORT, debug=False, use_reloader=False)

class KasaSistemi(ctk.CTk):
    def __init__(self):
        super().__init__()
        global kasa_arayuz_referansi
        kasa_arayuz_referansi = self

        self.title("SARAÇOĞLU DÖNER - POS")
        ctk.set_appearance_mode("dark") 
        self.geometry("1400x800")
        
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.arka_plana_gizle)
        keyboard.add_hotkey('ctrl+shift+alt+f2', self.arayuzu_goster_tetikleyici)

        threading.Thread(target=sunucuyu_baslat, daemon=True).start()

        self.menu_icecekler = menuyu_guncelle(baslangic_menu_icecekler)
        icecek_baslik = [{"ad": "🥤 İÇECEKLER", "is_header": True}]
        self.menu_et = menuyu_guncelle(baslangic_menu_et) + icecek_baslik + self.menu_icecekler
        self.menu_tavuk = menuyu_guncelle(baslangic_menu_tavuk) + icecek_baslik + self.menu_icecekler
        self.menu_kampanya = menuyu_guncelle(baslangic_menu_kampanya) + icecek_baslik + self.menu_icecekler

        self.aktif_siparisler = json_yukle(MASALAR_DOSYASI, [])
        self.sepet = []; self.ayarlar_modu = False 
        self.duzenlenen_adisyon_index = None; self.gunluk_sira_no = 1
        for s in self.aktif_siparisler:
            m_adi = str(s.get("musteri_adi", ""))
            if "Sira No:" in m_adi or "Sıra No:" in m_adi:
                try:
                    num = int(m_adi.split(":")[-1].strip())
                    if num >= self.gunluk_sira_no: self.gunluk_sira_no = num + 1
                except: pass
        self.mevcut_kolon_sayisi = 4 

        self.grid_columnconfigure(0, weight=65)
        self.grid_columnconfigure(1, weight=35, minsize=400)
        self.grid_rowconfigure(0, weight=1)

        self.sol_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.sol_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        tepe_kutu = ctk.CTkFrame(self.sol_frame, fg_color="transparent")
        tepe_kutu.pack(fill="x", padx=5, pady=5)
        self.baslik = ctk.CTkLabel(tepe_kutu, text="SARAÇOĞLU", font=("Arial", 28, "bold"), text_color="#FF9800")
        self.baslik.pack(side="left", padx=(5, 0))
        ctk.CTkLabel(tepe_kutu, text="v3.0.1", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=5, pady=(5, 0))

        bilgi_kutu = ctk.CTkFrame(tepe_kutu, fg_color="#1E1E1E", corner_radius=10); bilgi_kutu.pack(side="left", padx=5)
        gosterilecek_ip = KASA_IP if AKTIF_PORT == 5000 else f"{KASA_IP}:{AKTIF_PORT}"
        ctk.CTkLabel(bilgi_kutu, text=f"IP: {gosterilecek_ip}", font=("Arial", 14, "bold"), text_color="white").pack(side="left", padx=10, pady=5)
        self.garson_isik_lbl = ctk.CTkLabel(bilgi_kutu, text="🔴 Garson Yok", font=("Arial", 14, "bold"), text_color="#F44336")
        self.garson_isik_lbl.pack(side="left", padx=10, pady=5)

        btn_kutu = ctk.CTkFrame(tepe_kutu, fg_color="transparent"); btn_kutu.pack(side="right")
        self.guncelleme_btn = ctk.CTkButton(btn_kutu, text="🔄", font=("Arial", 20, "bold"), fg_color="#1565C0", hover_color="#0D47A1", command=self.guncellemeleri_kontrol_et, width=40, height=35)
        self.guncelleme_btn.pack(side="left", padx=3)
        self.ayarlar_btn = ctk.CTkButton(btn_kutu, text="⚙ Fiyat", font=("Arial", 16, "bold"), fg_color="#B71C1C", hover_color="#D32F2F", command=self.ayarlar_modu_degistir, width=70, height=35)
        self.ayarlar_btn.pack(side="left", padx=3)
        self.yazici_btn = ctk.CTkButton(btn_kutu, text="🖨 Yazıcı", font=("Arial", 16, "bold"), fg_color="#424242", command=self.yazici_ayari_penceresi, width=70, height=35)
        self.yazici_btn.pack(side="left", padx=3)
        self.kapat_btn = ctk.CTkButton(btn_kutu, text="🚪 Çıkış", font=("Arial", 16, "bold"), fg_color="#1E1E1E", hover_color="#b71c1c", command=self.sistemi_tamamen_kapat, width=70, height=35)
        self.kapat_btn.pack(side="left", padx=3)

        self.tab_frame = ctk.CTkFrame(self.sol_frame, fg_color="transparent"); self.tab_frame.pack(fill="x", padx=10, pady=10)
        self.sekme_butonlari = []
        self.sekmeler = [("🍽️ MASALAR", "masalar"), ("🥩 ET", self.menu_et), ("🍗 TAVUK", self.menu_tavuk), ("🔥 KAMPANYA", self.menu_kampanya), ("🥤 İÇECEK", self.menu_icecekler)]
        self.secili_sekme_index = 1
        
        for index, (baslik, data) in enumerate(self.sekmeler):
            btn = ctk.CTkButton(self.tab_frame, text=baslik, font=("Arial", 18, "bold"), height=60, fg_color="#E65100" if index==1 else "#2C2C2C", corner_radius=15, command=lambda d=data, i=index: self.sekme_degistir(d, i))
            btn.pack(side="left", expand=True, fill="both", padx=5)
            self.sekme_butonlari.append(btn)

        self.icerik_frame = ctk.CTkScrollableFrame(self.sol_frame, fg_color="transparent")
        self.icerik_frame._scrollbar.configure(width=35)
        self.icerik_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.sol_frame.bind("<Configure>", self.icerik_resize_oldu)
        
        self.sag_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=20)
        self.sag_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.sag_ust_baslik = ctk.CTkLabel(self.sag_frame, text="🧾 YENİ SİPARİŞ", font=("Arial", 22, "bold"), text_color="white")
        self.sag_ust_baslik.pack(pady=(15, 0))

        ust_giris_kutu = ctk.CTkFrame(self.sag_frame, fg_color="transparent"); ust_giris_kutu.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(ust_giris_kutu, text="Masa/İsim:", font=("Arial", 18, "bold")).pack(side="left")
        self.musteri_adi_entry = ctk.CTkEntry(ust_giris_kutu, font=("Arial", 22, "bold"), height=45)
        self.musteri_adi_entry.pack(side="right", fill="x", expand=True, padx=(15, 0))

        self.sepet_liste = ctk.CTkScrollableFrame(self.sag_frame, fg_color="#242424", corner_radius=15)
        self.sepet_liste._scrollbar.configure(width=35)
        self.sepet_liste.pack(fill="both", expand=True, padx=20, pady=5)
        
        alt_bilgi_kutu = ctk.CTkFrame(self.sag_frame, fg_color="#121212", corner_radius=15); alt_bilgi_kutu.pack(fill="x", padx=20, pady=15)
        self.toplam_lbl = ctk.CTkLabel(alt_bilgi_kutu, text="TOPLAM: 0 ₺", font=("Arial", 36, "bold"), text_color="#4CAF50")
        self.toplam_lbl.pack(pady=20)

        self.btn_frame = ctk.CTkFrame(self.sag_frame, fg_color="transparent"); self.btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.islem_satir1 = ctk.CTkFrame(self.btn_frame, fg_color="transparent"); self.islem_satir1.pack(fill="x", pady=5)
        self.sepet_iptal_btn = ctk.CTkButton(self.islem_satir1, text="❌ Temizle/İptal", font=("Arial", 20, "bold"), fg_color="#B71C1C", hover_color="#D32F2F", height=70, command=self.sepeti_temizle)
        self.sepet_iptal_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.sepet_yazdir_btn = ctk.CTkButton(self.islem_satir1, text="🖨️ Fiş Yazdır", font=("Arial", 20, "bold"), fg_color="#424242", hover_color="#616161", height=70, command=self.aktif_sepeti_yazdir)
        self.sepet_yazdir_btn.pack(side="right", expand=True, fill="x", padx=5)

        self.islem_satir2 = ctk.CTkFrame(self.btn_frame, fg_color="transparent"); self.islem_satir2.pack(fill="x", pady=5)
        
        self.kaydet_btn = ctk.CTkButton(self.islem_satir2, text="✔ MASAYI AÇ / KAYDET", font=("Arial", 22, "bold"), fg_color="#FF9800", text_color="black", hover_color="#E65100", height=80, command=self.masayi_kaydet)
        self.btn_guncelle = ctk.CTkButton(self.islem_satir2, text="🔄 GÜNCELLE", font=("Arial", 20, "bold"), fg_color="#1976D2", hover_color="#1565C0", height=80, command=self.masayi_guncelle)
        self.btn_kapat = ctk.CTkButton(self.islem_satir2, text="💸 ÖDENDİ / SİL", font=("Arial", 20, "bold"), fg_color="#2E7D32", hover_color="#1B5E20", height=80, command=self.hesabi_kapat)

        self.sekme_degistir(self.menu_et, 1)
        self.sepet_guncelle()
        self.isik_kontrol_dongusu()

    def arka_plana_gizle(self): self.withdraw()
    def sistemi_tamamen_kapat(self): os._exit(0)

    def guncellemeleri_kontrol_et(self):
        def islem():
            try:
                response = requests.get("https://api.github.com/repos/bilalgnd/saracapp/releases/latest", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tag = data.get("tag_name", "")
                    assets = data.get("assets", [])
                    apk_url = None
                    exe_url = None
                    for a in assets:
                        if a.get("name", "").endswith(".apk"): apk_url = a.get("browser_download_url")
                        if a.get("name", "").endswith(".exe"): exe_url = a.get("browser_download_url")
                    
                    mesajlar = []
                    if apk_url:
                        telefona_ozel_mesaj_gonder({"type": "apk_guncelleme", "url": apk_url})
                        mesajlar.append(f"Android APK güncellemesi ({tag}) bulundu ve bağlı garsonlara yollanıyor.")
                    
                    if exe_url:
                        mesajlar.append(f"Yeni Kasa EXE sürümü ({tag}) bulundu.")
                    
                    if mesajlar:
                        if exe_url:
                            cevap = messagebox.askyesno("Güncelleme", "\\n".join(mesajlar) + "\\n\\nKasa uygulamasının yeni sürümünü tarayıcıda indirmek ister misiniz?")
                            if cevap: webbrowser.open(exe_url)
                        else:
                            messagebox.showinfo("Güncelleme", "\\n".join(mesajlar))
                    else:
                        messagebox.showinfo("Güncelleme", f"En son yayınlanan sürüm ({tag}) için EXE veya APK dosyası bulunamadı.")
                else:
                    messagebox.showerror("Hata", "Güncellemeler kontrol edilirken bir hata oluştu. İnternet bağlantınızı kontrol edin veya daha sonra tekrar deneyin.")
            except Exception as e:
                messagebox.showerror("Hata", f"Bağlantı hatası: {e}")
        threading.Thread(target=islem, daemon=True).start()
    def arayuzu_goster_tetikleyici(self): self.after(0, self.arayuzu_goster_veya_gizle)
    def arayuzu_goster_veya_gizle(self):
        if self.winfo_viewable(): self.withdraw()
        else: self.deiconify(); self.state("zoomed"); self.focus_force(); self.lift()

    def icerik_resize_oldu(self, event):
        w = event.width
        yeni_kolon = max(1, w // 220) 
        if yeni_kolon > 6: yeni_kolon = 6 
        if yeni_kolon != self.mevcut_kolon_sayisi:
            self.mevcut_kolon_sayisi = yeni_kolon
            if hasattr(self, 'secili_sekme_index'):
                if self.secili_sekme_index == 0: self.acik_masalari_ciz()
                else: self.menuyu_ciz(self.sekmeler[self.secili_sekme_index][1])

    def isik_kontrol_dongusu(self):
        global son_kalp_atisi
        if time.time() - son_kalp_atisi < 5: self.garson_isik_lbl.configure(text="🟢 Garson: Çevrimiçi", text_color="#4CAF50")
        else: self.garson_isik_lbl.configure(text="🔴 Garson: Çevrimdışı", text_color="#F44336")
        self.after(2000, self.isik_kontrol_dongusu)

    def yazici_ayari_penceresi(self):
        popup = ctk.CTkToplevel(self); popup.title("Yazıcı Seçimi"); popup.geometry(f"500x250"); popup.attributes("-topmost", True); popup.grab_set()
        ctk.CTkLabel(popup, text="Windows Yazıcı Adını Girin", font=("Arial", 20, "bold")).pack(pady=20)
        yazici_girdi = ctk.CTkEntry(popup, font=("Arial", 20), width=350, height=50); yazici_girdi.insert(0, SISTEM_AYARLARI.get("YAZICI_ADI", "")); yazici_girdi.pack(pady=10)
        def kaydet(): SISTEM_AYARLARI["YAZICI_ADI"] = yazici_girdi.get().strip(); json_kaydet(AYAR_DOSYASI, SISTEM_AYARLARI); messagebox.showinfo("Başarılı", "Kaydedildi"); popup.destroy()
        ctk.CTkButton(popup, text="Kaydet", fg_color="#4CAF50", font=("Arial", 18, "bold"), height=50, command=kaydet).pack(pady=10)

    def masalari_diske_kaydet_ve_yay(self):
        json_kaydet(MASALAR_DOSYASI, self.aktif_siparisler); telefona_guncelleme_gonder()

    def telefondan_siparis_geldi(self, json_veri):
        musteri = json_veri["musteri_adi"].strip()
        saat = json_veri.get("saat", datetime.datetime.now().strftime("%H:%M"))
        if not musteri: musteri = f"Sıra No: {self.gunluk_sira_no}"; self.gunluk_sira_no += 1
        renk = json_veri.get("renk")
        self.aktif_siparisler = [m for m in self.aktif_siparisler if m.get("musteri_adi") != musteri]
        if len(json_veri.get("kalemler", [])) > 0:
            temiz = [{"ad": k["ad"], "gramaj": k["gramaj"], "fiyat": int(k["fiyat"]), "notlar": k.get("notlar", "")} for k in json_veri["kalemler"]]
            self.aktif_siparisler.insert(0, {"musteri_adi": musteri, "saat": saat, "kalemler": temiz, "toplam_tutar": int(json_veri["toplam_tutar"]), "durum": "Bekliyor", "renk": renk})
        self.masalari_diske_kaydet_ve_yay()
        if self.secili_sekme_index == 0: self.after(0, self.acik_masalari_ciz)

    def telefondan_silme_geldi(self, musteri_adi):
        self.aktif_siparisler = [a for a in self.aktif_siparisler if a["musteri_adi"] != musteri_adi]
        self.masalari_diske_kaydet_ve_yay()
        if self.secili_sekme_index == 0: self.after(0, self.acik_masalari_ciz)

    def ayarlar_modu_degistir(self):
        self.ayarlar_modu = not self.ayarlar_modu
        if self.ayarlar_modu: self.ayarlar_btn.configure(text="❌ Kapat", fg_color="#424242"); self.baslik.configure(text="⚙️ FİYAT AYARI", text_color="#F44336")
        else: self.ayarlar_btn.configure(text="⚙️ Fiyat", fg_color="#B71C1C"); self.baslik.configure(text="SARAÇOĞLU", text_color="#FF9800")
        self.sekme_degistir(self.sekmeler[self.secili_sekme_index][1], self.secili_sekme_index)

    def sekme_degistir(self, data, secili_index):
        self.secili_sekme_index = secili_index
        for i, btn in enumerate(self.sekme_butonlari): btn.configure(fg_color="#E65100" if i == secili_index else "#2C2C2C")
        if data == "masalar": self.acik_masalari_ciz()
        else: self.menuyu_ciz(data)

    def menuyu_ciz(self, menu_listesi):
        for w in self.icerik_frame.winfo_children(): w.destroy()
        for i in range(10): self.icerik_frame.grid_columnconfigure(i, weight=0); self.icerik_frame.grid_rowconfigure(i, weight=0)
        for i in range(self.mevcut_kolon_sayisi): self.icerik_frame.grid_columnconfigure(i, weight=1)

        satir, sutun = 0, 0
        for urun in menu_listesi:
            if urun.get("is_header"):
                if sutun != 0: satir += 1; sutun = 0
                lbl = ctk.CTkLabel(self.icerik_frame, text=urun["ad"], font=("Arial", 28, "bold"), text_color="#4FC3F7")
                lbl.grid(row=satir, column=0, columnspan=self.mevcut_kolon_sayisi, pady=(30, 10), sticky="w", padx=20)
                satir += 1
                continue

            ad_kucuk = urun['ad'].lower()
            if "tombik" in ad_kucuk: bg_renk = "#FF9800"; txt_renk = "black"; hov_renk = "#F57C00"
            elif "eski usul" in ad_kucuk: bg_renk = "#F44336"; txt_renk = "white"; hov_renk = "#D32F2F"
            elif "dürüm" in ad_kucuk: bg_renk = "#FFEB3B"; txt_renk = "black"; hov_renk = "#FBC02D"
            elif any(x in ad_kucuk for x in ["kola", "ayran", "su", "soda", "sprite", "fanta", "şalgam"]): bg_renk = "#0277BD"; txt_renk = "white"; hov_renk = "#01579B"
            else: bg_renk = "#37474F" if self.ayarlar_modu else "#1E1E1E"; txt_renk = "white"; hov_renk = "#455A64" if self.ayarlar_modu else "#333333"

            buton_yazisi = f"{urun['ad']}\n\n✏️ Fiyat" if self.ayarlar_modu else f"{urun['ad']}\n\n{urun['secenekler'][0]['fiyat']} ₺"
            btn = ctk.CTkButton(self.icerik_frame, text=buton_yazisi, font=("Arial", 22, "bold"), fg_color=bg_renk, hover_color=hov_renk, text_color=txt_renk, corner_radius=20, height=130, command=lambda u=urun: self.fiyat_penceresi_ac(u) if self.ayarlar_modu else self.siparis_penceresi_ac(u))
            btn.grid(row=satir, column=sutun, padx=10, pady=10, sticky="nsew")
            
            # Removed grid_rowconfigure to fix scrolling
            sutun += 1
            if sutun >= self.mevcut_kolon_sayisi: sutun = 0; satir += 1

    def acik_masalari_ciz(self):
        for w in self.icerik_frame.winfo_children(): w.destroy()
        if not self.aktif_siparisler:
            ctk.CTkLabel(self.icerik_frame, text="Şu an aktif sipariş / masa bulunmuyor.", font=("Arial", 24), text_color="gray").pack(pady=100)
            return

        for i in range(10): self.icerik_frame.grid_columnconfigure(i, weight=0); self.icerik_frame.grid_rowconfigure(i, weight=0)
        kolon = max(1, self.mevcut_kolon_sayisi - 1)
        for i in range(kolon): self.icerik_frame.grid_columnconfigure(i, weight=1)

        ust_frame = ctk.CTkFrame(self.icerik_frame, fg_color="transparent")
        ust_frame.grid(row=0, column=0, columnspan=kolon, sticky="ew", padx=12, pady=(12, 0))
        
        def tumunu_sil():
            if messagebox.askyesno("Onay", "Tum acik masalari silmek istediginize emin misiniz?"):
                self.aktif_siparisler.clear()
                self.masalari_diske_kaydet_ve_yay()
                self.acik_masalari_ciz()

        ctk.CTkButton(ust_frame, text="🗑 Tümünü Sil", fg_color="#D32F2F", hover_color="#B71C1C", font=("Arial", 16, "bold"), command=tumunu_sil).pack(side="right")

        satir, sutun = 1, 0
        for idx, adisyon in enumerate(self.aktif_siparisler):
            kart = ctk.CTkFrame(self.icerik_frame, fg_color="#1E1E1E", corner_radius=15, border_width=2, border_color="#333333", height=150)
            kart.grid(row=satir, column=sutun, padx=12, pady=12, sticky="nsew")
            kart.grid_propagate(False) 
            
            l1 = ctk.CTkLabel(kart, text=f"Masa:\n{adisyon['musteri_adi']}", font=("Arial", 22, "bold"), text_color="white")
            l1.place(relx=0.5, rely=0.3, anchor="center")
            l2 = ctk.CTkLabel(kart, text=f"{adisyon['toplam_tutar']} ₺", font=("Arial", 26, "bold"), text_color="#4CAF50")
            l2.place(relx=0.5, rely=0.65, anchor="center")
            l3 = ctk.CTkLabel(kart, text=f"Saat: {adisyon.get('saat', '')}", font=("Arial", 14), text_color="gray")
            l3.place(relx=0.5, rely=0.88, anchor="center")
            
            renk = adisyon.get("renk")
            if renk:
                renk_nokta = ctk.CTkFrame(kart, width=20, height=20, corner_radius=10, fg_color=renk, bg_color="#1E1E1E")
                renk_nokta.place(relx=0.9, rely=0.1, anchor="center")

            def tiklandi(e, i=idx): self.masayi_sepete_yukle(i)
            for widget in [kart, l1, l2, l3]:
                widget.bind("<Button-1>", tiklandi)
                widget.configure(cursor="hand2")
            if renk:
                renk_nokta.bind("<Button-1>", tiklandi)
                renk_nokta.configure(cursor="hand2")

            # Removed grid_rowconfigure to fix scrolling
            sutun += 1
            if sutun >= kolon: sutun = 0; satir += 1

    def siparis_penceresi_ac(self, urun):
        is_icecek = any(ic['ad'] == urun['ad'] for ic in self.menu_icecekler)
        w = 500 if is_icecek else 800
        h = 450 if is_icecek else 680
        popup = ctk.CTkToplevel(self); popup.title(f"Sipariş: {urun['ad']}")
        x = (self.winfo_screenwidth() - w) // 2; y = (self.winfo_screenheight() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}"); popup.attributes("-topmost", True); popup.grab_set()

        tepe = ctk.CTkFrame(popup, fg_color="#1E1E1E", corner_radius=15); tepe.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(tepe, text=urun['ad'], font=("Arial", 36, "bold"), text_color="#FF9800").pack(side="left", padx=20, pady=15)
        adet = ctk.IntVar(value=1); adet_kutu = ctk.CTkFrame(tepe, fg_color="#333333", corner_radius=15); adet_kutu.pack(side="right", padx=20)
        ctk.CTkButton(adet_kutu, text="-", width=60, height=60, font=("Arial", 36, "bold"), fg_color="transparent", command=lambda: self.guncelle_fiyat(popup, adet, -1)).pack(side="left")
        ctk.CTkLabel(adet_kutu, textvariable=adet, font=("Arial", 36, "bold")).pack(side="left", padx=20)
        ctk.CTkButton(adet_kutu, text="+", width=60, height=60, font=("Arial", 36, "bold"), fg_color="transparent", command=lambda: self.guncelle_fiyat(popup, adet, 1)).pack(side="left")

        govde = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        govde._scrollbar.configure(width=35)
        govde.pack(fill="both", expand=True, padx=10)
        
        self.modal_urun = urun; self.modal_adet = adet
        self.modal_secili_gramaj = ctk.StringVar(value=next((s['gr'] for s in urun['secenekler'] if s['gr'] == "100gr"), urun['secenekler'][0]['gr']))
        self.modal_anlik_fiyat = ctk.IntVar(value=next((s['fiyat'] for s in urun['secenekler'] if s['gr'] == "100gr"), urun['secenekler'][0]['fiyat']))
        self.modal_cikar = {m: ctk.BooleanVar(value=False) for m in ["Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu"]}
        self.modal_ucretli_ek = {e: ctk.BooleanVar(value=False) for e in UCRETLI_EKSTRALAR.keys()}
        self.modal_ucretsiz_ek = {e: ctk.BooleanVar(value=False) for e in ["Sade Et", "Soslu", "Gemi", "Kayık"]}
        self.modal_icecek = {ic['ad']: ctk.IntVar(value=0) for ic in self.menu_icecekler}

        def cip_olustur(parent, metin, var, true_color, false_color, yazi_renk="white", genislik=140, on_click=None):
            def toggle():
                if isinstance(var, ctk.BooleanVar): var.set(not var.get())
                elif isinstance(var, ctk.StringVar): var.set(metin)
                btn.configure(fg_color=true_color if (var.get() == True or var.get() == metin) else false_color)
                if on_click: on_click()
                self.guncelle_fiyat(popup) 
            
            btn = ctk.CTkButton(parent, text=metin, font=("Arial", 18, "bold"), width=genislik, height=50, fg_color=true_color if (var.get() == True or var.get() == metin) else false_color, text_color=yazi_renk, corner_radius=10, command=toggle)
            return btn, toggle



        ctk.CTkLabel(govde, text="Gramaj / Seçim:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        gr_satir = ctk.CTkFrame(govde, fg_color="transparent"); gr_satir.pack(fill="x", padx=10)
        self.gr_butonlari = []
        for s in urun['secenekler']:
            yazi = f"{s['fiyat']} ₺" if s['gr'] == "Standart" else f"{s['gr']} ({s['fiyat']}₺)"
            def secim_yap(g=s['gr'], f=s['fiyat']):
                self.modal_secili_gramaj.set(g); self.modal_anlik_fiyat.set(f)
                for btn, bg in self.gr_butonlari: btn.configure(fg_color="#4CAF50" if self.modal_secili_gramaj.get() == bg else "#424242")
                self.guncelle_fiyat(popup)
            b = ctk.CTkButton(gr_satir, text=yazi, font=("Arial", 18, "bold"), width=150, height=50, fg_color="#4CAF50" if self.modal_secili_gramaj.get() == s['gr'] else "#424242", corner_radius=10, command=secim_yap)
            b.pack(side="left", padx=5, pady=5)
            self.gr_butonlari.append((b, s['gr']))

        if not is_icecek:
            ctk.CTkLabel(govde, text="İçerik Çıkar:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            cik_sat = ctk.CTkFrame(govde, fg_color="transparent"); cik_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_cikar.items()):
                b, _ = cip_olustur(cik_sat, f"{ad} Yok", var, "#D32F2F", "#333333")
                b.grid(row=i//4, column=i%4, padx=5, pady=5)

            ctk.CTkLabel(govde, text="Ücretli Ekstralar:", font=("Arial", 18, "bold"), text_color="#FFD54F").pack(anchor="w", padx=10, pady=(20, 5))
            ek_sat = ctk.CTkFrame(govde, fg_color="transparent"); ek_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_ucretli_ek.items()):
                b, _ = cip_olustur(ek_sat, f"{ad} (+{UCRETLI_EKSTRALAR[ad]}₺)", var, "#FBC02D", "#333333", "black", 180)
                b.grid(row=i//4, column=i%4, padx=5, pady=5)

            ctk.CTkLabel(govde, text="Notlar:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            not_sat = ctk.CTkFrame(govde, fg_color="transparent"); not_sat.pack(fill="x", padx=10)
            for i, (ad, var) in enumerate(self.modal_ucretsiz_ek.items()):
                b, _ = cip_olustur(not_sat, ad, var, "#757575", "#333333")
                b.grid(row=i//4, column=i%4, padx=5, pady=5)

            ctk.CTkLabel(govde, text="Hızlı İçecek:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
            ic_sat = ctk.CTkFrame(govde, fg_color="transparent"); ic_sat.pack(fill="x", padx=10)
            for i, ic in enumerate(self.menu_icecekler):
                isim = ic['ad']; fy = ic['secenekler'][0]['fiyat']; fy_yz = f"(+{fy}₺)" if fy > 0 else ""
                k = ctk.CTkFrame(ic_sat, fg_color="#1E1E1E", corner_radius=10); k.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
                ctk.CTkLabel(k, text=f"{isim} {fy_yz}", font=("Arial", 18, "bold")).pack(side="left", padx=15)
                var = self.modal_icecek[isim]
                
                a_kt = ctk.CTkFrame(k, fg_color="#333333", corner_radius=8); a_kt.pack(side="right", padx=10, pady=5)
                def d(v=var, y=-1): v.set(max(0, v.get() + y)); self.guncelle_fiyat(popup)
                ctk.CTkButton(a_kt, text="-", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, -1)).pack(side="left")
                l = ctk.CTkLabel(a_kt, text="0", font=("Arial", 20, "bold"), width=30); l.pack(side="left")
                var.trace_add("write", lambda *args, lbl=l, v=var: lbl.configure(text=str(v.get()), text_color="#FF9800" if v.get()>0 else "white"))
                ctk.CTkButton(a_kt, text="+", width=40, font=("Arial", 22, "bold"), fg_color="transparent", command=lambda v=var: d(v, 1)).pack(side="left")

        ctk.CTkLabel(govde, text="Özel Not Gir:", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        self.modal_ozel_not = ctk.CTkEntry(govde, font=("Arial", 20), height=50, placeholder_text="Örn: Çok pişsin")
        self.modal_ozel_not.pack(fill="x", padx=10, pady=(0, 20))

        alt = ctk.CTkFrame(popup, fg_color="transparent"); alt.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(alt, text="❌ İptal", font=("Arial", 20), fg_color="transparent", text_color="gray", hover_color="#333333", height=70, command=popup.destroy).pack(side="left", expand=True, fill="x", padx=(0,10))
        self.modal_ekle_btn = ctk.CTkButton(alt, text="SEPETE EKLE", font=("Arial", 24, "bold"), fg_color="#FF9800", text_color="black", hover_color="#E65100", height=70, command=lambda: self.sepete_kalemleri_at(popup))
        self.modal_ekle_btn.pack(side="right", expand=True, fill="x")
        self.guncelle_fiyat(popup)

    def guncelle_fiyat(self, popup, adet_var=None, yon=0):
        if adet_var: adet_var.set(max(1, adet_var.get() + yon))
        b_fiyat = self.modal_anlik_fiyat.get()
        ek = sum(UCRETLI_EKSTRALAR[k] for k, v in self.modal_ucretli_ek.items() if v.get())
        ic_top = sum(v.get() * next((ic['secenekler'][0]['fiyat'] for ic in self.menu_icecekler if ic['ad'] == k), 0) for k, v in self.modal_icecek.items())
        toplam = ((b_fiyat + ek) * self.modal_adet.get()) + ic_top
        self.modal_ekle_btn.configure(text=f"SEPETE EKLE ({toplam} ₺)")

    def sepete_kalemleri_at(self, popup):
        n = []
        n.extend([f"{k} yok" for k, v in self.modal_cikar.items() if v.get()])
        n.extend([k for k, v in self.modal_ucretsiz_ek.items() if v.get()])
        n.extend([f"{k} eklendi" for k, v in self.modal_ucretli_ek.items() if v.get()])
        if self.modal_ozel_not.get().strip(): n.append(self.modal_ozel_not.get().strip())
        n_m = "Not: " + ", ".join(n) if n else ""
        
        b_fiyat = self.modal_anlik_fiyat.get() + sum(UCRETLI_EKSTRALAR[k] for k, v in self.modal_ucretli_ek.items() if v.get())

        for _ in range(self.modal_adet.get()):
            self.sepet.append({"ad": self.modal_urun['ad'], "gramaj": self.modal_secili_gramaj.get(), "fiyat": b_fiyat, "notlar": n_m})
        
        for k, v in self.modal_icecek.items():
            if v.get() > 0:
                ic_fiyat = next((ic['secenekler'][0]['fiyat'] for ic in self.menu_icecekler if ic['ad'] == k), 0)
                for _ in range(v.get()): self.sepet.append({"ad": k, "gramaj": "Standart", "fiyat": ic_fiyat, "notlar": ""})
                
        self.sepet_guncelle(); popup.destroy()

    def sepet_guncelle(self):
        for w in self.sepet_liste.winfo_children(): w.destroy()
        
        if self.duzenlenen_adisyon_index is not None:
            self.kaydet_btn.pack_forget()
            self.btn_guncelle.pack(side="left", expand=True, fill="x", padx=5)
            self.btn_kapat.pack(side="right", expand=True, fill="x", padx=5)
            self.sag_ust_baslik.configure(text="✏️ SİPARİŞ DÜZENLENİYOR", text_color="#FF9800")
        else:
            self.btn_guncelle.pack_forget()
            self.btn_kapat.pack_forget()
            self.kaydet_btn.pack(fill="x", expand=True, padx=5)
            self.sag_ust_baslik.configure(text="🧾 YENİ SİPARİŞ", text_color="white")

        gen_top = 0; gruplu = {}
        for i, k in enumerate(self.sepet):
            a = f"{k['ad']}_{k['gramaj']}_{k['notlar']}"
            if a not in gruplu: gruplu[a] = []
            gruplu[a].append({"index": i, "kalem": k})

        for a, liste in gruplu.items():
            ilk = liste[0]['kalem']; adt = len(liste); grp_fy = ilk['fiyat'] * adt; gen_top += grp_fy
            kart = ctk.CTkFrame(self.sepet_liste, fg_color="#1E1E1E", corner_radius=10); kart.pack(fill="x", pady=5)
            u_sat = ctk.CTkFrame(kart, fg_color="transparent"); u_sat.pack(fill="x", padx=10, pady=10)
            det = "" if ilk['gramaj'] == "Standart" else f"({ilk['gramaj']})"
            
            ctk.CTkLabel(u_sat, text=f"{adt}x {ilk['ad']} {det}", font=("Arial", 18, "bold")).pack(side="left")
            ctk.CTkLabel(u_sat, text=f"{grp_fy} ₺", font=("Arial", 20, "bold"), text_color="#4CAF50").pack(side="right")
            if ilk['notlar']: ctk.CTkLabel(kart, text=ilk['notlar'], font=("Arial", 14), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
            ctk.CTkButton(kart, text="🗑️", font=("Arial", 20), width=60, height=40, fg_color="#B71C1C", hover_color="#D32F2F", command=lambda idx=liste[0]['index']: self.kalem_sil(idx)).pack(anchor="e", padx=10, pady=(0,10))
        
        self.toplam_lbl.configure(text=f"TOPLAM: {gen_top} ₺")

    def kalem_sil(self, index): self.sepet.pop(index); self.sepet_guncelle()

    def sepeti_temizle(self): 
        self.sepet = [] 
        self.musteri_adi_entry.delete(0, 'end')
        self.duzenlenen_adisyon_index = None 
        self.sepet_guncelle()

    def masayi_kaydet(self):
        if not self.sepet: return 
        isim = self.musteri_adi_entry.get().strip()
        if not isim: isim = f"Sıra No: {self.gunluk_sira_no}"; self.gunluk_sira_no += 1
            
        self.aktif_siparisler.insert(0, {"musteri_adi": isim, "saat": datetime.datetime.now().strftime("%H:%M"), "kalemler": self.sepet.copy(), "toplam_tutar": sum(k['fiyat'] for k in self.sepet), "durum": "Bekliyor"})
        self.masalari_diske_kaydet_ve_yay()
        self.sepeti_temizle()
        if self.secili_sekme_index == 0: self.acik_masalari_ciz()

    def masayi_guncelle(self):
        idx = self.duzenlenen_adisyon_index
        if idx is not None and self.sepet:
            self.aktif_siparisler[idx]["musteri_adi"] = self.musteri_adi_entry.get().strip()
            self.aktif_siparisler[idx]["kalemler"] = self.sepet.copy()
            self.aktif_siparisler[idx]["toplam_tutar"] = sum(k['fiyat'] for k in self.sepet)
            self.masalari_diske_kaydet_ve_yay()
            self.sepeti_temizle()
            if self.secili_sekme_index == 0: self.acik_masalari_ciz()

    def hesabi_kapat(self):
        idx = self.duzenlenen_adisyon_index
        if idx is not None:
            self.aktif_siparisler.pop(idx)
            self.masalari_diske_kaydet_ve_yay()
            self.sepeti_temizle()
            if self.secili_sekme_index == 0: self.acik_masalari_ciz()

    def aktif_sepeti_yazdir(self):
        if not self.sepet: return
        isim = self.musteri_adi_entry.get().strip()
        if not isim: isim = f"Sıra No: {self.gunluk_sira_no}"; self.gunluk_sira_no += 1; self.musteri_adi_entry.insert(0, isim) 
        usb_fis_yazdir(isim, self.sepet, sum(k['fiyat'] for k in self.sepet), datetime.datetime.now().strftime("%H:%M"))

    def masayi_sepete_yukle(self, index):
        adisyon = self.aktif_siparisler[index]
        self.duzenlenen_adisyon_index = index 
        self.sepet = adisyon['kalemler'].copy()
        self.musteri_adi_entry.delete(0, 'end'); self.musteri_adi_entry.insert(0, adisyon['musteri_adi'])
        self.sepet_guncelle()

    def fiyat_penceresi_ac(self, urun):
        popup = ctk.CTkToplevel(self); popup.title(f"Fiyat Düzenle: {urun['ad']}")
        w, h = 400, 500; x = (self.winfo_screenwidth() - w) // 2; y = (self.winfo_screenheight() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}"); popup.attributes("-topmost", True); popup.grab_set() 

        ctk.CTkLabel(popup, text=urun['ad'], font=("Arial", 24, "bold"), text_color="#FF9800").pack(pady=15)
        kutu_frame = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        kutu_frame._scrollbar.configure(width=35)
        kutu_frame.pack(fill="both", expand=True, padx=15)
        girdi_kutulari = {}
        for sec in urun['secenekler']:
            satir = ctk.CTkFrame(kutu_frame, fg_color="transparent"); satir.pack(fill="x", pady=10)
            ctk.CTkLabel(satir, text=f"{sec['gr']}:", font=("Arial", 20, "bold")).pack(side="left", padx=10)
            kutu = ctk.CTkEntry(satir, font=("Arial", 20), width=100, height=40); kutu.insert(0, str(sec['fiyat'])); kutu.pack(side="right", padx=10)
            girdi_kutulari[sec['gr']] = kutu
            
        def kaydet():
            yeni_sec = []
            for sec in urun['secenekler']:
                y_f = girdi_kutulari[sec['gr']].get()
                yf_int = int(y_f) if y_f.isdigit() else sec['fiyat']
                yeni_sec.append({"gr": sec['gr'], "fiyat": yf_int})
                FIYAT_HAFIZASI[f"{urun['ad']}_{sec['gr']}"] = yf_int
            json_kaydet(VERI_DOSYASI, FIYAT_HAFIZASI); urun['secenekler'] = yeni_sec; popup.destroy()
            
        ctk.CTkButton(popup, text="✔ Kaydet", font=("Arial", 20, "bold"), fg_color="#2E7D32", height=60, command=kaydet).pack(fill="x", padx=15, pady=15)

if __name__ == "__main__":
    app = KasaSistemi()
    app.mainloop()
