import webbrowser
import customtkinter as ctk
import threading
import keyboard
import json
import time
import datetime
import logging
import os
import requests
from tkinter import messagebox
from saracapp_config import *
import saracapp_models as models
from saracapp_models import *
from saracapp_printer import print_receipt, get_available_printers, YAZICI_AKTIF
from saracapp_events import ui_event_queue
from saracapp_server import broadcast_update_to_phones, send_private_message_to_phone

MEVCUT_VERSIYON = "v4.1.12"
logger = logging.getLogger(__name__)

class KasaSistemi(ctk.CTk):
  def __init__(self):
    super().__init__()
    global kasa_arayuz_referansi
    kasa_arayuz_referansi = self

    self.title("SARAÇOĞLU DÖNER Dashboard")
    ctk.set_appearance_mode("dark")
    self.geometry("1366x768")
    self.minsize(1024, 600)

    # Thread-safe window management
    self.protocol("WM_DELETE_WINDOW", self.hide_to_background)
    self._show_ui_flag = False
    keyboard.add_hotkey("ctrl+shift+alt+f2", self.show_ui_trigger)
    keyboard.add_hotkey("ctrl+alt+s", self.show_ui_trigger)

    # Dashboard Grid: 3 columns (Sidebar, Main Content, Cart)
    self.grid_columnconfigure(0, weight=15, minsize=180) # Sidebar
    self.grid_columnconfigure(1, weight=60, minsize=450) # Main
    self.grid_columnconfigure(2, weight=25, minsize=320) # Cart
    self.grid_rowconfigure(0, weight=1)

    # Data initialization
    self.menu_drinks = update_menu(default_menu_drinks)
    icecek_baslik = [{"name": " İÇECEKLER", "is_header": True}]
    self.menu_meat = update_menu(default_menu_meat) + icecek_baslik + self.menu_drinks
    self.menu_chicken = update_menu(default_menu_chicken) + icecek_baslik + self.menu_drinks
    self.menu_campaign = update_menu(default_menu_campaign) + icecek_baslik + self.menu_drinks

    models.active_orders = load_json(TABLES_FILE, [])
    self.sepet = []; self.ayarlar_modu = False 
    self.duzenlenen_adisyon_index = None; self.daily_queue_no = 1
    for s in models.active_orders:
      m_adi = str(s.get("customer_name", ""))
      if "Sira No:" in m_adi or "Sıra No:" in m_adi:
        try:
          num = int(m_adi.split(":")[-1].strip())
          if num >= self.daily_queue_no: self.daily_queue_no = num + 1
        except: pass
    
    self.current_column_count = 4 

    # Build UI Panels
    self.build_sidebar()
    self.build_main_panel()
    self.build_cart_panel()

    # Initial state
    self.change_tab(self.menu_meat, 1)
    self.update_cart()
    self.light_control_loop()
    self.after(100, self.listen_queue)

  # ---------------- UI BUILDERS ----------------

  def build_sidebar(self):
    self.sidebar_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
    self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
    self.sidebar_frame.grid_rowconfigure(7, weight=1)
    self.sidebar_frame.grid_columnconfigure(0, weight=1)

    # Logo / Title
    logo_kutu = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
    logo_kutu.grid(row=0, column=0, sticky="ew", pady=(20, 30))
    ctk.CTkLabel(logo_kutu, text="SARAÇOĞLU", font=("Segoe UI", 28, "bold"), text_color="#FF9800").pack()
    ctk.CTkLabel(logo_kutu, text="POS DASHBOARD", font=("Segoe UI", 12, "bold"), text_color="gray").pack()

    # Navigation Buttons
    self.tab_buttons = []
    self.tabs = [
      (" MASALAR", "masalar"), 
      (" ET DÖNER", self.menu_meat), 
      (" TAVUK DÖNER", self.menu_chicken), 
      (" KAMPANYA", self.menu_campaign), 
      (" İÇECEK", self.menu_drinks)
    ]
    
    for idx, (baslik, data) in enumerate(self.tabs):
      btn = ctk.CTkButton(self.sidebar_frame, text=baslik, font=("Segoe UI", 14, "bold"), height=40, 
                corner_radius=15, fg_color="transparent", text_color="#FFFFFF", hover_color="#2A2A2A",
                anchor="w", command=lambda d=data, i=idx: self.change_tab(d, i))
      btn.grid(row=idx+1, column=0, sticky="ew", padx=15, pady=5)
      self.tab_buttons.append(btn)

    # Settings and Exit at bottom
    alt_kutu = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
    alt_kutu.grid(row=8, column=0, sticky="ew", pady=10)
    
    self.ayarlar_ana_btn = ctk.CTkButton(alt_kutu, text="⚙ Ayarlar", font=("Segoe UI", 16, "bold"), height=40,
                     fg_color="#1E1E1E", hover_color="#333333", command=self.open_settings_window)
    self.ayarlar_ana_btn.pack(fill="x", padx=15, pady=5)
    
    ctk.CTkButton(alt_kutu, text=" Çıkış", font=("Segoe UI", 16, "bold"), height=40,
           fg_color="#B71C1C", hover_color="#D32F2F", command=self.shutdown_system).pack(fill="x", padx=15, pady=5)


  def build_main_panel(self):
    self.main_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=20)
    self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 5), pady=10)
    
    # Header (Top Bar of Main Panel)
    self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
    self.header_frame.pack(fill="x", padx=20, pady=(15, 5))
    
    self.category_title = ctk.CTkLabel(self.header_frame, text="Kategori", font=("Segoe UI", 26, "bold"), text_color="white")
    self.category_title.pack(side="left")
    
    # Status Info on the right side of header
    status_kutu = ctk.CTkFrame(self.header_frame, fg_color="#2A2A2A", corner_radius=15)
    status_kutu.pack(side="right")
    gosterilecek_ip = CASH_REGISTER_IP if ACTIVE_PORT == 5000 else f"{CASH_REGISTER_IP}:{ACTIVE_PORT}"
    ctk.CTkLabel(status_kutu, text=f" IP: {gosterilecek_ip}", font=("Segoe UI", 14, "bold")).pack(side="left", padx=15, pady=8)
    self.waiter_light_lbl = ctk.CTkLabel(status_kutu, text=" Garson Yok", font=("Segoe UI", 14, "bold"), text_color="#F44336")
    self.waiter_light_lbl.pack(side="left", padx=(0, 15), pady=8)

    # Content Grid (Scrollable)
    self.content_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
    self.content_frame._scrollbar.configure(width=20)
    self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
    self.main_frame.bind("<Configure>", self.on_content_resize)


  def build_cart_panel(self):
    self.cart_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=20)
    self.cart_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
    
    self.sag_ust_baslik = ctk.CTkLabel(self.cart_frame, text=" YENİ SİPARİŞ", font=("Segoe UI", 16, "bold"), text_color="white")
    self.sag_ust_baslik.pack(pady=(20, 10))

    ust_giris_kutu = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
    ust_giris_kutu.pack(fill="x", padx=15, pady=5)
    self.musteri_adi_entry = ctk.CTkEntry(ust_giris_kutu, font=("Segoe UI", 16, "bold"), height=40, placeholder_text="Masa No / İsim")
    self.musteri_adi_entry.pack(fill="x", expand=True)

    self.sepet_liste = ctk.CTkScrollableFrame(self.cart_frame, fg_color="#121212", corner_radius=15)
    self.sepet_liste._scrollbar.configure(width=15)
    self.sepet_liste.pack(fill="both", expand=True, padx=15, pady=10)
    
    alt_bilgi_kutu = ctk.CTkFrame(self.cart_frame, fg_color="#121212", corner_radius=15)
    alt_bilgi_kutu.pack(fill="x", padx=15, pady=5)
    self.toplam_lbl = ctk.CTkLabel(alt_bilgi_kutu, text="0 ₺", font=("Segoe UI", 36, "bold"), text_color="#4CAF50")
    self.toplam_lbl.pack(pady=5)

    self.btn_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
    self.btn_frame.pack(fill="x", padx=15, pady=(0, 20))
    
    self.islem_satir1 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
    self.islem_satir1.pack(fill="x", pady=5)
    self.sepet_iptal_btn = ctk.CTkButton(self.islem_satir1, text=" İptal", font=("Segoe UI", 14, "bold"), fg_color="#424242", hover_color="#616161", height=32, command=self.clear_cart)
    self.sepet_iptal_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
    self.sepet_yazdir_btn = ctk.CTkButton(self.islem_satir1, text=" Yazdır", font=("Segoe UI", 14, "bold"), fg_color="#1976D2", hover_color="#1565C0", height=32, command=self.print_active_cart)
    self.sepet_yazdir_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

    self.islem_satir2 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
    self.islem_satir2.pack(fill="x", pady=2)
    self.kaydet_btn = ctk.CTkButton(self.islem_satir2, text=" MASAYI AÇ", font=("Segoe UI", 16, "bold"), fg_color="#FF9800", text_color="black", hover_color="#E65100", height=40, command=self.save_table)
    self.btn_guncelle = ctk.CTkButton(self.islem_satir2, text=" GÜNCELLE", font=("Segoe UI", 15, "bold"), fg_color="#0288D1", hover_color="#0277BD", height=40, command=self.update_table)
    self.btn_kapat = ctk.CTkButton(self.islem_satir2, text=" ÖDENDİ", font=("Segoe UI", 16, "bold"), fg_color="#2E7D32", hover_color="#1B5E20", height=40, command=self.close_bill)


  # ---------------- CORE LOGIC ----------------

  def listen_queue(self):
    if hasattr(self, '_show_ui_flag') and self._show_ui_flag:
      self._show_ui_flag = False
      self.toggle_ui_visibility()
      
    import queue
    try:
      while True:
        event = ui_event_queue.get_nowait()
        if event["action"] == "order_received": self.handle_incoming_order(event["data"])
        elif event["action"] == "order_deleted": self.handle_order_deleted(event["data"])
        elif event["action"] == "request_update": broadcast_update_to_phones(models.active_orders)
        elif event["action"] == "update_status": self.handle_update_status(event["data"])
        elif event["action"] == "print_receipt":
            m_adi = event["data"]["customer_name"]
            for a in models.active_orders:
                if a["customer_name"] == m_adi:
                    from saracapp_printer import print_receipt
                    print_receipt(m_adi, a.get('time', ''), a["items"], a["total_amount"])
                    self.show_pc_notification("Yazici", f"Fis yazdirildi: {m_adi}")
                    break
    except queue.Empty: pass
    self.after(100, self.listen_queue)

  def show_pc_notification(self, baslik, mesaj):
    try:
      import winsound, threading
      threading.Thread(target=lambda: winsound.Beep(1000, 300), daemon=True).start()
    except: pass
    toast = ctk.CTkToplevel(self)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(fg_color="#2A2A2A")
    w, h = 350, 90
    x = self.winfo_screenwidth() - w - 20
    y = self.winfo_screenheight() - h - 60
    toast.geometry(f"{w}x{h}+{x}+{y}")
    ctk.CTkLabel(toast, text=baslik, font=("Segoe UI", 16, "bold"), text_color="#4CAF50").pack(pady=(10,5))
    ctk.CTkLabel(toast, text=mesaj, font=("Segoe UI", 14), text_color="white").pack(pady=(0,10))
    self.after(3000, toast.destroy)

  def hide_to_background(self): self.withdraw()
  def shutdown_system(self): os._exit(0)

  def show_ui_trigger(self): 
    self._show_ui_flag = True
    
  def toggle_ui_visibility(self):
    try:
      if self.winfo_viewable(): self.withdraw()
      else: 
        self.deiconify()
        self.state("zoomed")
        self.focus_force()
        self.lift()
    except: pass

  def on_content_resize(self, event):
    if hasattr(self, '_resize_timer'):
      self.after_cancel(self._resize_timer)
    self._resize_timer = self.after(250, lambda w=event.width: self._actual_resize(w))

  def _actual_resize(self, w):
    yeni_kolon = max(1, w // 200) 
    if yeni_kolon > 6: yeni_kolon = 6 
    if yeni_kolon != self.current_column_count:
      self.current_column_count = yeni_kolon
      if hasattr(self, 'selected_tab_index'):
        if self.selected_tab_index == 0: self.draw_open_tables()
        else: self.draw_menu(self.tabs[self.selected_tab_index][1])

  def light_control_loop(self):
    import saracapp_server as server
    if time.time() - server.last_heartbeat < 5: self.waiter_light_lbl.configure(text=" Garson: Çevrimiçi", text_color="#4CAF50")
    else: self.waiter_light_lbl.configure(text=" Garson: Çevrimdışı", text_color="#F44336")
    self.after(2000, self.light_control_loop)

  def save_and_broadcast_tables(self):
    save_json(TABLES_FILE, models.active_orders)
    broadcast_update_to_phones(models.active_orders)

  def handle_incoming_order(self, json_data):
    musteri = json_data["customer_name"].strip()
    time_str = json_data.get("time", datetime.datetime.now().strftime("%H:%M"))
    if not musteri: musteri = f"Sıra No: {self.daily_queue_no}"; self.daily_queue_no += 1
    color = json_data.get("color")
    
    existing_idx = None
    for i, m in enumerate(models.active_orders):
      if m.get("customer_name") == musteri:
        existing_idx = i
        break
        
    temiz = [{"name": k["name"], "portion": k["portion"], "price": int(k["price"]), "notes": k.get("notes", "")} for k in json_data.get("items", [])]
    
    if existing_idx is not None:
      models.active_orders[existing_idx]["items"] = temiz
      models.active_orders[existing_idx]["total_amount"] = int(json_data.get("total_amount", sum(k["price"] for k in temiz)))
      models.active_orders[existing_idx]["status"] = "waiting"
    else:
      models.active_orders.insert(0, {"customer_name": musteri, "time": time_str, "items": temiz, "total_amount": int(json_data.get("total_amount", sum(k["price"] for k in temiz))), "status": "waiting", "color": color})
      
    self.save_and_broadcast_tables()
    if self.selected_tab_index == 0: self.after(0, self.draw_open_tables)

  def handle_order_deleted(self, customer_name):
    for i in range(len(models.active_orders)):
      if models.active_orders[i]["customer_name"] == customer_name:
        models.active_orders.pop(i)
        self.save_and_broadcast_tables()
        if self.selected_tab_index == 0: self.after(0, self.draw_open_tables)
        break

  def handle_update_status(self, data):
    isim = data.get("customer_name")
    durum = data.get("status")
    for adisyon in models.active_orders:
      if adisyon.get("customer_name") == isim:
        adisyon["status"] = durum
        break
    self.save_and_broadcast_tables()
    if self.selected_tab_index == 0: self.after(0, self.draw_open_tables)

  # ---------------- UI UPDATERS & RENDERERS ----------------

  def change_tab(self, data, secili_index):
    self.selected_tab_index = secili_index
    for i, btn in enumerate(self.tab_buttons):
      if i == secili_index:
        btn.configure(fg_color="#FF9800", text_color="black")
        self.category_title.configure(text=self.tabs[i][0])
      else:
        btn.configure(fg_color="transparent", text_color="#FFFFFF")
    
    if data == "masalar": self.draw_open_tables()
    else: self.draw_menu(data)


  def get_drink_color(self, name):
    n = name.lower()
    if "kutu kola" in n or "sise kola" in n: return "#B71C1C", "#D32F2F"
    if "ayran" in n and "acik" not in n: return "#827717", "#9E9D24"
    if "acik ayran" in n: return "#9E9D24", "#AFB42B"
    if "cola zero" in n: return "#212121", "#424242"
    if "salgam" in n: return "#6A1B9A", "#8E24AA"
    if "su" == n: return "#01579B", "#0288D1"
    if "sprite" in n: return "#1B5E20", "#2E7D32"
    if "fanta" in n: return "#E65100", "#F57C00"
    if "soda" in n: return "#2E7D32", "#388E3C"
    return "#0288D1", "#03A9F4"

  def draw_menu(self, menu_listesi):
    for w in self.content_frame.winfo_children(): w.destroy()
    for i in range(10): self.content_frame.grid_columnconfigure(i, weight=0, uniform=""); self.content_frame.grid_rowconfigure(i, weight=0)
    for i in range(self.current_column_count): self.content_frame.grid_columnconfigure(i, weight=1, uniform="group1")

    row, column = 0, 0
    for product in menu_listesi:
      if product.get("is_header"):
        if column != 0: row += 1; column = 0
        lbl = ctk.CTkLabel(self.content_frame, text=product["name"], font=("Segoe UI", 22, "bold"), text_color="#9E9E9E")
        lbl.grid(row=row, column=0, columnspan=self.current_column_count, pady=(30, 10), sticky="w", padx=20)
        row += 1
        continue

      # Modern Card Colors
      name_lower = product['name'].lower()
      if "tombik" in name_lower: bg_color = "#F57C00"; hov_color = "#FF9800"
      elif "eski usul" in name_lower: bg_color = "#D32F2F"; hov_color = "#F44336"
      elif "durum" in name_lower: bg_color = "#F9A825"; hov_color = "#FBC02D" # Koyu Sari
      elif any(x in name_lower for x in ["porsiyon", "beyti", "iskender", "pilav ustu"]): bg_color = "#B71C1C"; hov_color = "#D32F2F" # Kirmizi
      elif "hatay" in name_lower: bg_color = "#D2B48C"; hov_color = "#F5DEB3"
      elif "biga" in name_lower: bg_color = "#1565C0"; hov_color = "#1976D2"
      elif any(x in name_lower for x in ["kola", "ayran", "su", "soda", "sprite", "fanta", "salgam", "zero"]): bg_color, hov_color = self.get_drink_color(product["name"])
      else: bg_color = "#2C2C2C"; hov_color = "#3D3D3D"
      
      kart = ctk.CTkFrame(self.content_frame, fg_color=bg_color, corner_radius=20, height=80)
      kart.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
      kart.grid_propagate(False)

      ad_lbl = ctk.CTkLabel(kart, text=product['name'], font=("Segoe UI", 16, "bold"), text_color="white", wraplength=180)
      ad_lbl.place(relx=0.5, rely=0.35, anchor="center")
      
      fiyat_yazisi = "Fiyat Düzenle" if self.ayarlar_modu else f"{product['options'][0]['price']} ₺"
      fiy_lbl = ctk.CTkLabel(kart, text=fiyat_yazisi, font=("Segoe UI", 14, "bold"), text_color="#E0E0E0" if not self.ayarlar_modu else "#FFD54F")
      fiy_lbl.place(relx=0.5, rely=0.75, anchor="center")

      # Click binding
      widget_state = {"start_y": 0, "was_dragged": False, "is_pressed": False}

      def on_press(e, state=widget_state):
        state["was_dragged"] = False
        state["is_pressed"] = True
        state["start_y"] = e.y_root

      def on_motion(e, state=widget_state):
        dy = e.y_root - state["start_y"]
        if abs(dy) > 10:
          state["was_dragged"] = True
          self.content_frame._parent_canvas.yview_scroll(int(-dy/5), "units")
          state["start_y"] = e.y_root

      def on_release(e, u=product, state=widget_state):
        if not state.get("is_pressed", False): return
        state["is_pressed"] = False
        if not state["was_dragged"]:
          if self.ayarlar_modu: self.open_price_window(u)
          else: self.open_order_window(u)
      
      kart.bind("<ButtonPress-1>", on_press)
      kart.bind("<B1-Motion>", on_motion)
      kart.bind("<ButtonRelease-1>", on_release)
      ad_lbl.bind("<ButtonPress-1>", on_press)
      ad_lbl.bind("<B1-Motion>", on_motion)
      ad_lbl.bind("<ButtonRelease-1>", on_release)
      fiy_lbl.bind("<ButtonPress-1>", on_press)
      fiy_lbl.bind("<B1-Motion>", on_motion)
      fiy_lbl.bind("<ButtonRelease-1>", on_release)
      for w in [kart, ad_lbl, fiy_lbl]: w.configure(cursor="hand2")

      column += 1
      if column >= self.current_column_count: column = 0; row += 1

  def draw_open_tables(self):
    for w in self.content_frame.winfo_children(): w.destroy()
    if not models.active_orders:
      ctk.CTkLabel(self.content_frame, text="Şu an aktif sipariş / masa bulunmuyor.", font=("Segoe UI", 22), text_color="gray").pack(pady=50)
      return

    for i in range(10): self.content_frame.grid_columnconfigure(i, weight=0, uniform=""); self.content_frame.grid_rowconfigure(i, weight=0)
    kolon = self.current_column_count
    for i in range(kolon): self.content_frame.grid_columnconfigure(i, weight=1, uniform="group1")

    ust_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
    ust_frame.grid(row=0, column=0, columnspan=kolon, sticky="ew", padx=12, pady=(0, 10))
    
    def delete_all():
      if messagebox.askyesno("Onay", "Tüm açık masaları silmek istediğinize emin misiniz?"):
        models.active_orders.clear()
        self.save_and_broadcast_tables()
        self.draw_open_tables()

    ctk.CTkButton(ust_frame, text=" Tümünü Sil", fg_color="#D32F2F", hover_color="#B71C1C", font=("Segoe UI", 16, "bold"), height=40, command=delete_all).pack(side="right")

    row, column = 1, 0
    for idx, adisyon in enumerate(models.active_orders):
      is_edit_mode = (getattr(self, "duzenlenen_adisyon_index", None) == idx)
      ad_color = adisyon.get("color")
      bg_color = "#333333" if is_edit_mode else "#242424"
      b_color = "#FF9800" if is_edit_mode else (ad_color if ad_color else "#3A3A3A")
      border_w = 2 if is_edit_mode else (2 if ad_color else 1) # CTK bug: border_w > 2 causes corner rendering artifacts
      kart = ctk.CTkFrame(self.content_frame, fg_color=bg_color, corner_radius=15, border_width=border_w, border_color=b_color, height=100)
      kart.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
      kart.grid_propagate(False) 
      
      if is_edit_mode:
        x_btn = ctk.CTkButton(kart, text="✖", font=("Segoe UI", 12, "bold"), width=24, height=24, corner_radius=12, fg_color="#D32F2F", hover_color="#B71C1C", text_color="white", command=self.clear_cart)
        x_btn.place(relx=0.92, rely=0.18, anchor="center")

      if adisyon.get("status") == "prepared":
        tik_lbl = ctk.CTkLabel(kart, text="✔", font=("Segoe UI", 24, "bold"), text_color="#4CAF50")
        tik_lbl.place(relx=0.15, rely=0.25, anchor="center")

      l1_rely = 0.20 if is_edit_mode else 0.3
      
      name_str = adisyon['customer_name']
      f_size = 18
      if len(name_str) > 22: f_size = 12
      elif len(name_str) > 16: f_size = 14
      elif len(name_str) > 12: f_size = 16
      if is_edit_mode: f_size -= 2
      
      l1 = ctk.CTkLabel(kart, text=name_str, font=("Segoe UI", f_size, "bold"), text_color=ad_color if ad_color else "white")
      l1.place(relx=0.5, rely=l1_rely, anchor="center")
      if is_edit_mode:
        ctk.CTkLabel(kart, text="(Düzenleniyor)", font=("Segoe UI", 11, "bold"), text_color="#FF9800").place(relx=0.5, rely=0.40, anchor="center")
      
      l2_rely = 0.65
      l2 = ctk.CTkLabel(kart, text=f"{adisyon['total_amount']} ₺", font=("Segoe UI", 20 if is_edit_mode else 22, "bold"), text_color="#4CAF50")
      l2.place(relx=0.5, rely=l2_rely, anchor="center")
      
      l3_rely = 0.88 if is_edit_mode else 0.9
      l3 = ctk.CTkLabel(kart, text=f"Saat: {adisyon.get('time', '')}", font=("Segoe UI", 11 if is_edit_mode else 12), text_color="gray")
      l3.place(relx=0.5, rely=l3_rely, anchor="center")
      
      color = adisyon.get("color")
      if color:
        renk_nokta = ctk.CTkFrame(kart, width=20, height=20, corner_radius=10, fg_color=color, bg_color=bg_color)
        renk_nokta.place(relx=0.08 if is_edit_mode else 0.9, rely=0.18 if is_edit_mode else 0.15, anchor="center")

      # Long press variables
      widget_state = {"long_press_job": None, "was_long_pressed": False, "start_y": 0, "was_dragged": False, "is_pressed": False}

      def on_press(e, i=idx, state=widget_state):
        state["was_long_pressed"] = False
        state["was_dragged"] = False
        state["is_pressed"] = True
        state["start_y"] = e.y_root
        state["long_press_job"] = self.after(500, lambda: do_long_press(i, state))

      def do_long_press(i, state):
        if state["was_dragged"]: return
        state["was_long_pressed"] = True
        import winsound
        winsound.Beep(1000, 100) # Give haptic/audio feedback
        self.toggle_table_prepared(i)

      def on_motion(e, state=widget_state):
        dy = e.y_root - state["start_y"]
        if abs(dy) > 10:
            state["was_dragged"] = True
            if state["long_press_job"] is not None:
                self.after_cancel(state["long_press_job"])
                state["long_press_job"] = None
            self.content_frame._parent_canvas.yview_scroll(int(-dy/5), "units")
            state["start_y"] = e.y_root

      def on_release(e, i=idx, state=widget_state):
        if not state.get("is_pressed", False): return
        state["is_pressed"] = False
        if state["long_press_job"] is not None:
          self.after_cancel(state["long_press_job"])
          state["long_press_job"] = None
        if not state["was_long_pressed"] and not state["was_dragged"]:
          self.load_table_to_cart(i)

      for widget in [kart, l1, l2, l3]:
        widget.bind("<ButtonPress-1>", on_press)
        widget.bind("<B1-Motion>", on_motion)
        widget.bind("<ButtonRelease-1>", on_release)
        widget.configure(cursor="hand2")
      if color:
        renk_nokta.bind("<ButtonPress-1>", on_press)
        renk_nokta.bind("<B1-Motion>", on_motion)
        renk_nokta.bind("<ButtonRelease-1>", on_release)
        renk_nokta.configure(cursor="hand2")

      column += 1
      if column >= kolon: column = 0; row += 1

  def update_cart(self):
    for w in self.sepet_liste.winfo_children(): w.destroy()
    
    if self.duzenlenen_adisyon_index is not None:
      self.kaydet_btn.pack_forget()
      self.btn_guncelle.pack(side="left", expand=True, fill="x", padx=5)
      self.btn_kapat.pack(side="right", expand=True, fill="x", padx=5)
      self.sag_ust_baslik.configure(text="✏️ DÜZENLENİYOR", text_color="#FF9800")
    else:
      self.btn_guncelle.pack_forget()
      self.btn_kapat.pack_forget()
      self.kaydet_btn.pack(fill="x", expand=True, padx=5)
      self.sag_ust_baslik.configure(text=" YENİ SİPARİŞ", text_color="white")

    gen_top = 0; gruplu = {}
    for i, k in enumerate(self.sepet):
      a = f"{k['name']}_{k['portion']}_{k['notes']}"
      if a not in gruplu: gruplu[a] = []
      gruplu[a].append({"index": i, "kalem": k})

    for a, liste in gruplu.items():
      ilk = liste[0]['kalem']; adt = len(liste); grp_fy = ilk['price'] * adt; gen_top += grp_fy
      kart = ctk.CTkFrame(self.sepet_liste, fg_color="#1E1E1E", corner_radius=12)
      kart.pack(fill="x", pady=6)
      
      u_sat = ctk.CTkFrame(kart, fg_color="transparent")
      u_sat.pack(fill="x", padx=15, pady=(10, 5))
      det = "" if ilk['portion'] == "Standart" else f"({ilk['portion']})"
      
      ctk.CTkLabel(u_sat, text=f"{adt}x {ilk['name']} {det}", font=("Segoe UI", 14, "bold"), text_color="white").pack(side="left")
      ctk.CTkLabel(u_sat, text=f"{grp_fy} ₺", font=("Segoe UI", 16, "bold"), text_color="#4CAF50").pack(side="right")
      
      if ilk['notes']: 
        n_lbl = ctk.CTkLabel(kart, text=ilk['notes'], font=("Segoe UI", 13), text_color="#9E9E9E")
        n_lbl.pack(anchor="w", padx=15, pady=(0, 5))
      else:
        n_lbl = None
      
      alt_sat = ctk.CTkFrame(kart, fg_color="transparent")
      alt_sat.pack(fill="x", padx=10, pady=(0, 10))
      ctk.CTkButton(alt_sat, text="Sil", font=("Segoe UI", 14), width=50, height=28, fg_color="#B71C1C", hover_color="#D32F2F", corner_radius=6, command=lambda idx=liste[0]['index']: self.delete_cart_item(idx)).pack(side="right")
      
      # Add scroll drag binding to cart items
      state = {"start_y": 0}
      def c_on_press(e, s=state): s["start_y"] = e.y_root
      def c_on_motion(e, s=state):
          dy = e.y_root - s["start_y"]
          if abs(dy) > 10:
              self.sepet_liste._parent_canvas.yview_scroll(int(-dy/5), "units")
              s["start_y"] = e.y_root
      
      for w in [kart, u_sat, alt_sat]:
          w.bind("<ButtonPress-1>", c_on_press)
          w.bind("<B1-Motion>", c_on_motion)
      for w in u_sat.winfo_children():
          w.bind("<ButtonPress-1>", c_on_press)
          w.bind("<B1-Motion>", c_on_motion)
      if n_lbl:
          n_lbl.bind("<ButtonPress-1>", c_on_press)
          n_lbl.bind("<B1-Motion>", c_on_motion)
    
    self.toplam_lbl.configure(text=f"{gen_top} ₺")

  # ---------------- MODALS & POPUPS ----------------

  def open_settings_window(self):
    popup = ctk.CTkToplevel(self)
    popup.title("⚙ Ayarlar Paneli")
    popup.geometry("600x500")
    popup.transient(self)
    popup.grab_set()

    ctk.CTkLabel(popup, text="Yönetim & Ayarlar", font=("Segoe UI", 18, "bold"), text_color="#FF9800").pack(pady=10)
    
    grid_frame = ctk.CTkFrame(popup, fg_color="transparent")
    grid_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def enable_price_mode():
      self.ayarlar_modu = True
      self.ayarlar_ana_btn.configure(text=" Fiyat Ayarı Kapat", fg_color="#B71C1C", command=disable_price_mode)
      self.category_title.configure(text="⚙ FİYAT DÜZENLEME", text_color="#F44336")
      self.change_tab(self.tabs[self.selected_tab_index][1], self.selected_tab_index)
      popup.destroy()

    def disable_price_mode():
      self.ayarlar_modu = False
      self.ayarlar_ana_btn.configure(text="⚙ Ayarlar", fg_color="#1E1E1E", command=self.open_settings_window)
      self.change_tab(self.tabs[self.selected_tab_index][1], self.selected_tab_index)

    def func_btn(parent, text, color, command):
      return ctk.CTkButton(parent, text=text, font=("Segoe UI", 14, "bold"), height=70, fg_color=color, command=command)

    b1 = func_btn(grid_frame, "✏ Menü Fiyat Ayarı", "#D32F2F", enable_price_mode)
    b2 = func_btn(grid_frame, " Yazıcı Seçimi", "#424242", self.open_printer_settings)
    b3 = func_btn(grid_frame, " Web Paneli", "#3949AB", self.open_web_pos)
    b4 = func_btn(grid_frame, " Spotify Bağlan", "#1DB954", self.open_music_settings)
    b5 = func_btn(grid_frame, " Güncellemeler", "#1565C0", self.check_updates)

    b1.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    b2.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
    b3.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
    b4.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
    b5.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
    
    grid_frame.grid_columnconfigure(0, weight=1)
    grid_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(popup, text="Kapat", font=("Segoe UI", 16), fg_color="#1E1E1E", height=40, command=popup.destroy).pack(pady=5, padx=30, fill="x")

  def open_order_window(self, product):
    is_icecek = any(ic['name'] == product['name'] for ic in self.menu_drinks)
    w = 600
    
    s_w = self.winfo_screenwidth()
    s_h = self.winfo_screenheight()
    
    h = 450 if is_icecek else min(720, s_h - 100)
    
    popup = ctk.CTkToplevel(self)
    popup.title("Sipariş Özelleştirme")
    
    x = (s_w - w) // 2
    y = (s_h - h) // 2
    
    if y < 0: y = 20
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.attributes("-topmost", True)
    popup.grab_set()
    popup.configure(fg_color="#181818")

    # HEADER
    top_frame = ctk.CTkFrame(popup, fg_color="transparent", height=40)
    top_frame.pack(fill="x", padx=15, pady=(15, 5))
    top_frame.pack_propagate(False)
    ctk.CTkLabel(top_frame, text=product['name'], font=("Segoe UI", 24, "bold"), text_color="white").pack(side="left")
    
    adet = ctk.IntVar(value=1)
    qty_box = ctk.CTkFrame(top_frame, fg_color="#2A2A2A", corner_radius=8, width=100, height=35)
    qty_box.pack(side="right")
    qty_box.pack_propagate(False)
    ctk.CTkButton(qty_box, text="−", width=35, font=("Segoe UI", 22, "bold"), fg_color="transparent", hover_color="#444", command=lambda: self.update_price(popup, adet, -1)).pack(side="left")
    ctk.CTkLabel(qty_box, textvariable=adet, font=("Segoe UI", 18, "bold"), text_color="#FF9800", width=30).pack(side="left")
    ctk.CTkButton(qty_box, text="+", width=35, font=("Segoe UI", 22, "bold"), fg_color="transparent", hover_color="#444", command=lambda: self.update_price(popup, adet, 1)).pack(side="left")

    # Dynamic Scaling variables based on screen resolution
    is_small_screen = s_h < 800
    chip_h = 28 if is_small_screen else 35
    chip_f = 11 if is_small_screen else 13
    drink_h = 35 if is_small_screen else 50
    drink_f = 11 if is_small_screen else 12
    pad_y = 2 if is_small_screen else 4

    # BODY
    govde = ctk.CTkScrollableFrame(popup, fg_color="transparent")
    govde._scrollbar.configure(width=0) # Hide scrollbar as requested
    govde.pack(fill="both", expand=True, padx=15)
    
    self.modal_urun = product
    self.modal_adet = adet
    self.modal_secili_gramaj = ctk.StringVar(value=next((s['portion'] for s in product['options'] if s['portion'] == "100gr"), product['options'][0]['portion']))
    self.modal_anlik_fiyat = ctk.IntVar(value=next((s['price'] for s in product['options'] if s['portion'] == "100gr"), product['options'][0]['price']))
    
    tum_icerikler = ["Sogansiz", "Domatessiz", "Patatessiz", "Ketcapsiz", "Mayonezsiz", "Tursusuz", 
             "Soganli", "Domatesli", "Patatesli", "Ketcapli", "Mayonezli", "Tursulu"]
    
    self.modal_chipler = {c: ctk.BooleanVar(value=False) for c in tum_icerikler}
    self.modal_ucretli_ek = {e: ctk.BooleanVar(value=False) for e in PAID_EXTRAS.keys()}
    self.modal_ucretsiz_ek = {e: ctk.BooleanVar(value=False) for e in ["Sade Et", "Soslu", "Gemi", "Kayık"]}
    self.modal_icecek = {ic['name']: ctk.IntVar(value=0) for ic in self.menu_drinks}

    def create_chip(parent, metin, var, secili_renk="#4CAF50", yazi_renk="white", on_click=None):
        def toggle():
          if isinstance(var, ctk.BooleanVar): var.set(not var.get())
          elif isinstance(var, ctk.StringVar): var.set(metin)
          is_sel = (var.get() == True or var.get() == metin)
          guncel_bg = secili_renk if is_sel else "transparent"
          btn.configure(fg_color=guncel_bg, text_color=yazi_renk if is_sel else secili_renk)
          if on_click: on_click()
          self.update_price(popup) 
        
        is_sel = (var.get() == True or var.get() == metin)
        btn = ctk.CTkButton(parent, text=metin, font=("Segoe UI", chip_f, "bold"), height=chip_h, 
                  fg_color=secili_renk if is_sel else "transparent", 
                  border_color=secili_renk, border_width=2,
                  text_color=yazi_renk if is_sel else secili_renk, 
                  corner_radius=8, command=toggle)
        return btn, toggle

    # --- GRAMAJ KARTI (No Header) ---
    gr_satir = ctk.CTkFrame(govde, fg_color="transparent")
    gr_satir.pack(fill="x", pady=(5, 5))
    self.gr_butonlari = []
    for i, s in enumerate(product['options']):
      yazi = f"{s['price']} ₺" if s['portion'] == "Standart" else f"{s['portion']} ({s['price']}₺)"
      def make_selection(g=s['portion'], f=s['price']):
        self.modal_secili_gramaj.set(g); self.modal_anlik_fiyat.set(f)
        for btn, bg in self.gr_butonlari: 
          btn.configure(fg_color="#4CAF50" if self.modal_secili_gramaj.get() == bg else "transparent",
                 text_color="white" if self.modal_secili_gramaj.get() == bg else "#B0B0B0")
        self.update_price(popup)
      b = ctk.CTkButton(gr_satir, text=yazi, font=("Segoe UI", chip_f), height=chip_h, 
               fg_color="#4CAF50" if self.modal_secili_gramaj.get() == s['portion'] else "transparent", 
               border_color="#444", border_width=1,
               text_color="white" if self.modal_secili_gramaj.get() == s['portion'] else "#B0B0B0", 
               corner_radius=8, command=make_selection)
      b.grid(row=i//3, column=i%3, padx=4, pady=pad_y, sticky="ew")
      gr_satir.grid_columnconfigure(i%3, weight=1)
      self.gr_butonlari.append((b, s['portion']))

    if not is_icecek:
      # --- COMBINED ICERIK & SERVIS (No Header) ---
      ic_satir = ctk.CTkFrame(govde, fg_color="transparent")
      ic_satir.pack(fill="x", pady=(0, 5))
      
      def exclusive(isim):
        if isim.endswith("siz"):
          tersi = isim.replace("siz", "li")
          if tersi == "Tursulu": tersi = "Tursulu" 
          elif tersi == "Soganli": tersi = "Soganli"
        elif isim.endswith("suz"):
          tersi = "Tursulu"
        elif isim.endswith("li") or isim.endswith("lu"):
          tersi = isim.replace("li", "siz").replace("lu", "suz")
        
        if tersi in self.modal_chipler and self.modal_chipler[isim].get():
          self.modal_chipler[tersi].set(False)
          self.icerik_btn_refs[tersi].configure(fg_color="transparent", text_color="#B0B0B0")

      self.icerik_btn_refs = {}
      # Combine all 18 chips
      all_chips = tum_icerikler + list(self.modal_ucretsiz_ek.keys()) + list(self.modal_ucretli_ek.keys())
      for i, isim in enumerate(all_chips):
        renk = "#4CAF50"
        y_renk = "white"
        if isim.endswith("siz") or isim.endswith("suz"): renk = "#9C27B0"
        elif isim.endswith("li") or isim.endswith("lu"): renk = "#E91E63"
        elif isim in ["Cheddar", "Kasarli"]: renk = "#FBC02D"; y_renk = "black"
        else: renk = "#00838F"
        
        if isim in self.modal_chipler:
          var = self.modal_chipler[isim]
          b, _ = create_chip(ic_satir, isim, var, secili_renk=renk, yazi_renk=y_renk, on_click=lambda a=isim: exclusive(a))
        elif isim in self.modal_ucretsiz_ek:
          var = self.modal_ucretsiz_ek[isim]
          b, _ = create_chip(ic_satir, isim, var, secili_renk=renk, yazi_renk=y_renk)
        else:
          var = self.modal_ucretli_ek[isim]
          b, _ = create_chip(ic_satir, isim, var, secili_renk=renk, yazi_renk=y_renk)
        
        b.grid(row=i//3, column=i%3, padx=4, pady=pad_y, sticky="ew")
        ic_satir.grid_columnconfigure(i%3, weight=1)
        self.icerik_btn_refs[isim] = b

      # --- HIZLI ICECEK (No Header) ---
      ic_blok = ctk.CTkFrame(govde, fg_color="transparent")
      ic_blok.pack(fill="x", pady=(5, 5))
      
      for i, ic in enumerate(self.menu_drinks):
        isim = ic['name']
        bg_c, _ = self.get_drink_color(isim)
        
        b = ctk.CTkButton(ic_blok, text=isim, font=("Segoe UI", drink_f, "bold"), height=drink_h, 
                 fg_color=bg_c, hover_color=bg_c, text_color="white", corner_radius=8)
        b.grid(row=i//4, column=i%4, padx=4, pady=pad_y, sticky="ew")
        ic_blok.grid_columnconfigure(i%4, weight=1)
        
        def on_btn_press(event, name=isim, btn=b):
          self._btn_basildi_zaman = event.time
          
        def on_btn_release(event, name=isim, btn=b, org_ad=isim):
          fark = event.time - self._btn_basildi_zaman
          var = self.modal_icecek[name]
          if fark > 400: # Long press
            var.set(max(0, var.get() - 1))
          else: # Short tap
            var.set(var.get() + 1)
          
          if var.get() > 0:
            btn.configure(text=f"{org_ad}\n({var.get()})", border_width=2, border_color="#FF9800")
          else:
            btn.configure(text=org_ad, border_width=0)
          self.update_price(popup)

        b.bind("<ButtonPress-1>", on_btn_press)
        b.bind("<ButtonRelease-1>", on_btn_release)
        b.bind("<Button-3>", lambda e, name=isim, btn=b, org_ad=isim: (
          self.modal_icecek[name].set(max(0, self.modal_icecek[name].get() - 1)),
          btn.configure(text=f"{org_ad}\n({self.modal_icecek[name].get()})" if self.modal_icecek[name].get() > 0 else org_ad, border_width=2 if self.modal_icecek[name].get() > 0 else 0, border_color="#FF9800"),
          self.update_price(popup)
        ))

    # Ozel Not
    ctk.CTkLabel(govde, text="Özel Sipariş Notu:", font=("Segoe UI", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=5)
    self.modal_ozel_not = ctk.CTkTextbox(govde, font=("Segoe UI", 14), height=40 if is_small_screen else 80, corner_radius=8, fg_color="#222", border_color="#444", border_width=1)
    self.modal_ozel_not.pack(fill="x", pady=(0, 10))

    # Footer Actions
    alt = ctk.CTkFrame(popup, fg_color="transparent", height=45 if is_small_screen else 60)
    alt.pack(fill="x", padx=15, pady=(0, 10))
    alt.pack_propagate(False)
    self.modal_ekle_btn = ctk.CTkButton(alt, text="SEPETE EKLE", font=("Segoe UI", 16 if is_small_screen else 18, "bold"), fg_color="#FF9800", text_color="black", hover_color="#F57C00", height=45 if is_small_screen else 50, corner_radius=10, command=lambda: self.add_items_to_cart(popup))
    self.modal_ekle_btn.pack(fill="x", expand=True)
    self.update_price(popup)

  # ---------------- ACTION BINDINGS ----------------
  
  def delete_cart_item(self, index): self.sepet.pop(index); self.update_cart()
  def clear_cart(self): 
    was_editing = self.duzenlenen_adisyon_index is not None
    self.sepet = []; self.musteri_adi_entry.delete(0, 'end'); self.duzenlenen_adisyon_index = None; self.update_cart()
    if was_editing and getattr(self, 'selected_tab_index', -1) == 0: self.draw_open_tables()

  def save_table(self):
    if not self.sepet: return 
    isim = self.musteri_adi_entry.get().strip()
    if not isim: isim = f"Sıra No: {self.daily_queue_no}"; self.daily_queue_no += 1
    models.active_orders.insert(0, {"customer_name": isim, "time": datetime.datetime.now().strftime("%H:%M"), "items": self.sepet.copy(), "total_amount": sum(k['price'] for k in self.sepet), "status": "waiting"})
    self.save_and_broadcast_tables(); self.clear_cart()
    if self.selected_tab_index == 0: self.draw_open_tables()
  def update_table(self):
    idx = self.duzenlenen_adisyon_index
    if idx is not None and self.sepet:
      models.active_orders[idx]["customer_name"] = self.musteri_adi_entry.get().strip()
      models.active_orders[idx]["items"] = self.sepet.copy()
      models.active_orders[idx]["total_amount"] = sum(k['price'] for k in self.sepet)
      self.save_and_broadcast_tables(); self.clear_cart()
      if self.selected_tab_index == 0: self.draw_open_tables()
  def close_bill(self):
    idx = self.duzenlenen_adisyon_index
    if idx is not None:
      models.active_orders.pop(idx)
      self.save_and_broadcast_tables(); self.clear_cart()
      if self.selected_tab_index == 0: self.draw_open_tables()
  def print_active_cart(self):
    if not self.sepet: return
    isim = self.musteri_adi_entry.get().strip()
    if not isim: isim = "Masa/Belirsiz"
    from datetime import datetime
    saat = datetime.now().strftime("%H:%M")
    try:
      print_receipt(isim, saat, self.sepet, sum(k['price'] for k in self.sepet))
      self.show_pc_notification("Yazici", "Yazdirma komutu gonderildi.")
    except Exception as e:
      self.show_pc_notification("Yazıcı Hatası", str(e))
  def load_table_to_cart(self, index):
    self.duzenlenen_adisyon_index = index
    adisyon = models.active_orders[index]
    self.sepet = adisyon["items"].copy()
    self.musteri_adi_entry.delete(0, "end")
    self.musteri_adi_entry.insert(0, adisyon.get("customer_name", ""))
    self.update_cart()
    if getattr(self, 'selected_tab_index', -1) == 0: self.draw_open_tables()

  def toggle_table_prepared(self, index):
    try:
      adisyon = models.active_orders[index]
      current_status = adisyon.get("status", "waiting")
      new_status = "waiting" if current_status == "prepared" else "prepared"
      
      adisyon["status"] = new_status
      self.save_and_broadcast_tables()
      if self.selected_tab_index == 0: self.draw_open_tables()
    except IndexError:
      pass

  def toggle_prepared(self):
    if self.duzenlenen_adisyon_index is not None:
      self.toggle_table_prepared(self.duzenlenen_adisyon_index)

  def update_price(self, popup, adet_var=None, yon=0):
    if adet_var: adet_var.set(max(1, adet_var.get() + yon))
    b_fiyat = self.modal_anlik_fiyat.get()
    ek = sum(PAID_EXTRAS[k] for k, v in self.modal_ucretli_ek.items() if v.get())
    ic_top = sum(v.get() * next((ic['options'][0]['price'] for ic in self.menu_drinks if ic['name'] == k), 0) for k, v in self.modal_icecek.items())
    toplam = ((b_fiyat + ek) * self.modal_adet.get()) + ic_top
    self.modal_ekle_btn.configure(text=f"SEPETE EKLE ({toplam} ₺)")

  def add_items_to_cart(self, popup):
    n = []
    if hasattr(self, 'modal_chipler'):
      n.extend([k for k, v in self.modal_chipler.items() if v.get()])
    elif hasattr(self, 'modal_cikar'): # Fallback logic just in case
      n.extend([k + "sız" if k != "Tursu" else "Turşusuz" for k, v in self.modal_cikar.items() if v.get()])
      for k, v in self.modal_ekle.items():
        if v.get():
          ek_ad = k + "lı" if not k.endswith("es") else k + "li"
          if k == "Tursu": ek_ad = "Turşulu"
          if k == "Sogan": ek_ad = "Soğanlı"
          if k == "Ketcap": ek_ad = "Ketçaplı"
          n.append(ek_ad)
    
    if hasattr(self, 'modal_ucretsiz_ek'): n.extend([k for k, v in self.modal_ucretsiz_ek.items() if v.get()])
    if hasattr(self, 'modal_ucretli_ek'):
      n.extend([f"{k}" for k, v in self.modal_ucretli_ek.items() if v.get() if k in ["Cheddar", "Kasarli"]])
      n.extend([f"{k} eklendi" for k, v in self.modal_ucretli_ek.items() if v.get() if k not in ["Cheddar", "Kasarli"]])
      b_fiyat = self.modal_anlik_fiyat.get() + sum(PAID_EXTRAS[k] for k, v in self.modal_ucretli_ek.items() if v.get())
    else:
      b_fiyat = self.modal_anlik_fiyat.get()
    
    if hasattr(self, 'modal_ozel_not'):
      try:
        not_metni = self.modal_ozel_not.get("0.0", "end").strip()
      except TypeError:
        not_metni = self.modal_ozel_not.get().strip()
      if not_metni: n.append(not_metni)
      
    n_m = "Not: " + ", ".join(n) if n else ""
    
    for _ in range(self.modal_adet.get()):
      self.sepet.append({"name": self.modal_urun['name'], "portion": self.modal_secili_gramaj.get(), "price": b_fiyat, "notes": n_m})
      
    if hasattr(self, 'modal_icecek'):
      for k, v in self.modal_icecek.items():
        if v.get() > 0:
          ic_fiyat = next((ic['options'][0]['price'] for ic in self.menu_drinks if ic['name'] == k), 0)
          for _ in range(v.get()): self.sepet.append({"name": k, "portion": "Standart", "price": ic_fiyat, "notes": ""})
    self.update_cart(); popup.destroy()

  def open_price_window(self, product):
    popup = ctk.CTkToplevel(self)
    popup.title(f"Fiyat Düzenle: {product['name']}")
    popup.geometry("400x300")
    popup.attributes("-topmost", True); popup.grab_set()

    ctk.CTkLabel(popup, text=f"{product['name']} Fiyatı", font=("Segoe UI", 16, "bold")).pack(pady=10)
    yeni_fiyat = ctk.IntVar(value=product['options'][0]['price'])
    e = ctk.CTkEntry(popup, textvariable=yeni_fiyat, font=("Segoe UI", 18, "bold"), width=150, justify="center")
    e.pack(pady=10)

    def kaydet():
      try:
        val = int(e.get())
        for s in product['options']: s['price'] = val
        save_json(MENU_DOSYASI, {"drinks": default_menu_drinks, "meat": default_menu_meat, "chicken": default_menu_chicken, "campaign": default_menu_campaign})
        self.change_tab(self.tabs[self.selected_tab_index][1], self.selected_tab_index)
        popup.destroy()
      except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")

    ctk.CTkButton(popup, text="KAYDET", font=("Segoe UI", 14, "bold"), fg_color="#4CAF50", height=40, command=kaydet).pack(pady=10)

  # ---------------- SETTINGS & OTHERS ----------------
  def open_web_pos(self): webbrowser.open("http://localhost:5000/")
  def check_updates(self):
    def islem():
      try:
        response = requests.get("https://api.github.com/repos/bilalgnd/saracapp/releases/latest", timeout=5)
        if response.status_code == 200:
          data = response.json()
          tag = data.get("tag_name", "")
          assets = data.get("assets", [])
          apk_url = None; exe_url = None
          for a in assets:
            if a.get("name", "").endswith(".apk"): apk_url = a.get("browser_download_url")
            if a.get("name", "").endswith(".exe"): exe_url = a.get("browser_download_url")
          def ask_ui():
            panel = ctk.CTkToplevel(self)
            panel.title("Güncelleme"); panel.geometry("400x300"); panel.attributes("-topmost", True); panel.grab_set()
            def send_to_mobile():
                def mobile_yolla():
                  try: send_private_message_to_phone({"type": "apk_guncelleme", "url": apk_url})
                  except: pass
                mobile_yolla()
            if tag == MEVCUT_VERSIYON or tag == MEVCUT_VERSIYON.replace("v", ""):
              ctk.CTkLabel(panel, text=f"Güncel ({tag})", font=("Segoe UI", 22, "bold"), text_color="#2196F3").pack(pady=10)
              if apk_url: ctk.CTkButton(panel, text="Garsonlara Güncelleme Gönder", command=send_to_mobile).pack(pady=10)
            else:
              ctk.CTkLabel(panel, text=f"Yeni Versiyon: {tag}", font=("Segoe UI", 22, "bold"), text_color="#4CAF50").pack(pady=10)
              if exe_url: ctk.CTkButton(panel, text="PC Exe İndir", command=lambda: webbrowser.open(exe_url)).pack(pady=10)
              if apk_url: ctk.CTkButton(panel, text="Garsonlara Gönder", fg_color="#F44336", command=send_to_mobile).pack(pady=10)
          self.after(0, ask_ui)
      except: pass
    threading.Thread(target=islem, daemon=True).start()

  def open_music_settings(self):
    popup = ctk.CTkToplevel(self); popup.title("Spotify Connect"); popup.geometry("500x300"); popup.grab_set()
    ctk.CTkLabel(popup, text="Spotify ID:").pack(pady=(15,0))
    client_id_var = ctk.StringVar(value=SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_ID", ""))
    ctk.CTkEntry(popup, textvariable=client_id_var, width=400).pack()
    ctk.CTkLabel(popup, text="Spotify Secret:").pack(pady=(10,0))
    client_secret_var = ctk.StringVar(value=SYSTEM_SETTINGS.get("SPOTIFY_CLIENT_SECRET", ""))
    ctk.CTkEntry(popup, textvariable=client_secret_var, width=400).pack()
    def kaydet():
      SYSTEM_SETTINGS["SPOTIFY_CLIENT_ID"] = client_id_var.get().strip()
      SYSTEM_SETTINGS["SPOTIFY_CLIENT_SECRET"] = client_secret_var.get().strip()
      save_json(SETTINGS_FILE, SYSTEM_SETTINGS)
      webbrowser.open("http://127.0.0.1:5000/spotify/login")
      popup.destroy()
    ctk.CTkButton(popup, text="Kaydet & Bağlan", command=kaydet, fg_color="#1DB954").pack(pady=10)

  def open_printer_settings(self):
    popup = ctk.CTkToplevel(self); popup.title("Yazıcı Seçimi"); popup.geometry("400x200"); popup.grab_set()
    try:
      import win32print
      printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    except: printers = []
    if not printers: printers = ["Bulunamadi"]
    secili_yazici = ctk.StringVar(value=SYSTEM_SETTINGS.get("YAZICI_ADI", printers[0] if printers else ""))
    ctk.CTkOptionMenu(popup, values=printers, variable=secili_yazici, width=300).pack(pady=10)
    def kaydet():
      SYSTEM_SETTINGS["YAZICI_ADI"] = secili_yazici.get()
      save_json(SETTINGS_FILE, SYSTEM_SETTINGS)
      popup.destroy()
    ctk.CTkButton(popup, text="Kaydet", command=kaydet).pack()
    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # Logo / Title
        logo_kutu = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_kutu.grid(row=0, column=0, sticky="ew", pady=(30, 40))
        ctk.CTkLabel(logo_kutu, text="SARAÇOĞLU", font=("Segoe UI", 26, "bold"), text_color="#FF9800").pack(anchor="center")
        ctk.CTkLabel(logo_kutu, text="POS DASHBOARD", font=("Segoe UI", 12, "bold"), text_color="gray").pack(anchor="center")

        # Navigation Buttons
        self.tab_buttons = []
        self.tabs = [
            ("MASALAR", "masalar"), 
            ("ET DÖNER", self.menu_meat), 
            ("TAVUK DÖNER", self.menu_chicken), 
            ("KAMPANYA", self.menu_campaign), 
            ("İÇECEK", self.menu_drinks)
        ]
        
        for idx, (baslik, data) in enumerate(self.tabs):
            btn = ctk.CTkButton(self.sidebar_frame, text=baslik, font=("Segoe UI", 15, "bold"), height=45, 
                    corner_radius=10, fg_color="transparent", text_color="#FFFFFF", hover_color="#2A2A2A",
                    anchor="center", command=lambda d=data, i=idx: self.change_tab(d, i))
            btn.grid(row=idx+1, column=0, sticky="ew", padx=20, pady=5)
            self.tab_buttons.append(btn)

        # Settings and Exit at bottom
        alt_kutu = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        alt_kutu.grid(row=8, column=0, sticky="ew", pady=20)
        
        self.ayarlar_ana_btn = ctk.CTkButton(alt_kutu, text="Ayarlar", font=("Segoe UI", 15, "bold"), height=45, corner_radius=10,
                        fg_color="#1E1E1E", hover_color="#333333", anchor="center", command=self.open_settings_window)
        self.ayarlar_ana_btn.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(alt_kutu, text="Çıkış", font=("Segoe UI", 15, "bold"), height=45, corner_radius=10,
               fg_color="#B71C1C", hover_color="#D32F2F", anchor="center", command=self.shutdown_system).pack(fill="x", padx=20, pady=5)


