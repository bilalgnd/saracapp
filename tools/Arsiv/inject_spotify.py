import codecs
import re

kasa_pyw = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(kasa_pyw, 'r', 'utf-8') as f:
    text = f.read()

# We will add requests and urllib.parse.urlencode if not present, but requests is already there maybe?
# Actually, let's just insert the new flask routes before `def sunucuyu_baslat():`

flask_routes_code = """import base64
import requests
from urllib.parse import urlencode

@flask_app.route('/spotify/login')
def spotify_login():
    SPOTIFY_CLIENT_ID = SISTEM_AYARLARI.get("SPOTIFY_CLIENT_ID", "")
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
    
    SPOTIFY_CLIENT_ID = SISTEM_AYARLARI.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = SISTEM_AYARLARI.get("SPOTIFY_CLIENT_SECRET", "")
    
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
        SISTEM_AYARLARI["SPOTIFY_ACCESS_TOKEN"] = data.get("access_token")
        SISTEM_AYARLARI["SPOTIFY_REFRESH_TOKEN"] = data.get("refresh_token")
        ayarlari_kaydet()
        return "Spotify basariyla baglandi! Kasa uygulamasina donebilirsiniz. Bu pencereyi kapatabilirsiniz."
    else:
        return f"Hata: {res.text}"

@flask_app.route('/spotify/token')
def spotify_token():
    access_token = SISTEM_AYARLARI.get("SPOTIFY_ACCESS_TOKEN", "")
    refresh_token = SISTEM_AYARLARI.get("SPOTIFY_REFRESH_TOKEN", "")
    if not access_token or not refresh_token:
        return jsonify({"error": "not_logged_in"}), 401
        
    test_res = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"})
    if test_res.status_code == 401:
        SPOTIFY_CLIENT_ID = SISTEM_AYARLARI.get("SPOTIFY_CLIENT_ID", "")
        SPOTIFY_CLIENT_SECRET = SISTEM_AYARLARI.get("SPOTIFY_CLIENT_SECRET", "")
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
            SISTEM_AYARLARI["SPOTIFY_ACCESS_TOKEN"] = data.get("access_token")
            if "refresh_token" in data:
                SISTEM_AYARLARI["SPOTIFY_REFRESH_TOKEN"] = data.get("refresh_token")
            ayarlari_kaydet()
            access_token = SISTEM_AYARLARI["SPOTIFY_ACCESS_TOKEN"]
        else:
            return jsonify({"error": "refresh_failed"}), 401
            
    return jsonify({"access_token": access_token})

def sunucuyu_baslat():"""

text = text.replace("def sunucuyu_baslat():", flask_routes_code)

# Replace muzik_ayari_penceresi content completely
old_muzik_func_pattern = re.compile(r'def muzik_ayari_penceresi\(self\):.*?def isik_kontrol_dongusu', re.DOTALL)

new_muzik_func = """def muzik_ayari_penceresi(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Spotify Connect Ayarlari")
        popup.geometry("600x350")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Spotify Developer Bilgileri:", font=("Arial", 18, "bold")).pack(pady=(15, 5))
        
        ctk.CTkLabel(popup, text="Client ID:").pack()
        client_id_var = ctk.StringVar(value=SISTEM_AYARLARI.get("SPOTIFY_CLIENT_ID", ""))
        ctk.CTkEntry(popup, textvariable=client_id_var, font=("Arial", 14), width=500).pack(pady=5)
        
        ctk.CTkLabel(popup, text="Client Secret:").pack()
        client_secret_var = ctk.StringVar(value=SISTEM_AYARLARI.get("SPOTIFY_CLIENT_SECRET", ""))
        ctk.CTkEntry(popup, textvariable=client_secret_var, font=("Arial", 14), width=500).pack(pady=5)

        def kaydet_ve_baglan():
            SISTEM_AYARLARI["SPOTIFY_CLIENT_ID"] = client_id_var.get().strip()
            SISTEM_AYARLARI["SPOTIFY_CLIENT_SECRET"] = client_secret_var.get().strip()
            ayarlari_kaydet()
            import webbrowser
            webbrowser.open("http://127.0.0.1:5000/spotify/login")
            popup.destroy()

        ctk.CTkButton(popup, text="Kaydet ve Spotify'a Baglan", font=("Arial", 16, "bold"), fg_color="#1DB954", hover_color="#1AA34A", text_color="white", command=kaydet_ve_baglan, height=45).pack(pady=20)
        ctk.CTkButton(popup, text="Kapat", font=("Arial", 14), fg_color="#424242", hover_color="#616161", command=popup.destroy).pack(pady=5)

    def isik_kontrol_dongusu"""

text = old_muzik_func_pattern.sub(new_muzik_func, text)

# update version
text = text.replace('MEVCUT_VERSIYON = "v4.1.2"', 'MEVCUT_VERSIYON = "v4.1.3"')
text = text.replace('ctk.CTkLabel(tepe_kutu, text="v4.1.2"', 'ctk.CTkLabel(tepe_kutu, text="v4.1.3"')
text = text.replace('if tag == "v4.1.2" or tag == "4.1.2":', 'if tag == "v4.1.3" or tag == "4.1.3":')

with codecs.open(kasa_pyw, 'w', 'utf-8') as f:
    f.write(text)

print("kasa_app.pyw backend updated for Spotify Web SDK.")
