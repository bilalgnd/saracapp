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
    
    komut = [
        "pyinstaller",
        "--name=saracapp",
        "--noconsole",
        "--onefile",
        "--icon=logo.ico",
        "--add-data=templates;templates",
        "--add-data=static;static",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=urllib3.packages.six.moves",
        dosya_yolu
    ]
    
    subprocess.run(komut, cwd=calisma_dizini)