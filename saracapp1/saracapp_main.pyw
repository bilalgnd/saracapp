import multiprocessing
import threading
from saracapp_server import run_server
from saracapp_config import ACTIVE_PORT

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # Sunucuyu arka planda baslat (Web & Mobil erisimi icin)
    threading.Thread(target=run_server, args=('0.0.0.0', ACTIVE_PORT), daemon=True).start()
    
    from saracapp_ui import KasaSistemi
    app = KasaSistemi()
    app.mainloop()
