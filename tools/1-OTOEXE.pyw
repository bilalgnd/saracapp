import tkinter as tk
from tkinter import filedialog
import subprocess
import os

root = tk.Tk()
root.withdraw()

dosya_yolu = filedialog.askopenfilename(
    title="Derlenecek .py dosyasını seçin",
    filetypes=[("Python Dosyaları", "*.py *.pyw")]
)

if dosya_yolu:
    calisma_dizini = os.path.dirname(dosya_yolu)
    
    # Find version from saracapp_ui.py
    version = ""
    ui_path = os.path.join(calisma_dizini, "saracapp_ui.py")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            for line in f:
                if "MEVCUT_VERSIYON" in line:
                    version = line.split("=")[1].strip().replace('"', '').replace("'", "").replace("v", "")
                    break

    exe_name = f"saracapp{version}"

    komut = [
        "pyinstaller",
        f"--name={exe_name}",
        "--noconsole",
        "--onefile",
        "--icon=tools/logo.ico",
        "--add-data=templates;templates",
        "--add-data=static;static",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=urllib3.packages.six.moves",
        "--distpath=0-versions",
        dosya_yolu
    ]
    
    subprocess.run(komut, cwd=calisma_dizini)