import logging
import traceback
from saracapp_models import SYSTEM_SETTINGS

logger = logging.getLogger(__name__)

YAZICI_AKTIF = False
try:
    import win32print
    YAZICI_AKTIF = True
except ImportError:
    pass

def print_receipt(customer_name, time, items, total_amount):
    yazici_adi = SYSTEM_SETTINGS.get("YAZICI_ADI", "")
    if not YAZICI_AKTIF or not yazici_adi:
        logger.warning("Yazici aktif degil veya yazici adi ayarlanmamis. Yazdirma iptal edildi.")
        return

    def clean_tr(text):
        return text.replace("ğ","g").replace("Ğ","G").replace("ı","i").replace("İ","I").replace("ö","o").replace("Ö","O").replace("ş","s").replace("Ş","S").replace("ü","u").replace("Ü","U").replace("ç","c").replace("Ç","C")

    ALIGN_CENTER = b"\x1b\x61\x01"
    ALIGN_LEFT = b"\x1b\x61\x00"
    SIZE_DEV = b"\x1d\x21\x22"
    SIZE_NORMAL = b"\x1d\x21\x00"
    BOLD_ON = b"\x1b\x45\x01"
    BOLD_OFF = b"\x1b\x45\x00"
    CUT = b"\x1d\x56\x42\x00"

    fis = ALIGN_CENTER + SIZE_DEV + BOLD_ON + b"SARACOGLU DONER\n\n"
    fis += SIZE_NORMAL + BOLD_OFF + b"Tarih/Saat: " + time.encode("ascii", errors="replace") + b"\n"
    fis += b"Masa: " + clean_tr(customer_name).encode("ascii", errors="replace") + b"\n"
    fis += b"------------------------------------------\n"
    fis += ALIGN_LEFT
    
    fis_text = "SARACOGLU DONER\n\n"
    fis_text += f"Tarih/Saat: {time}\n"
    fis_text += f"Masa: {customer_name}\n"
    fis_text += "------------------------------------------\n"

    for k in items:
        isim = clean_tr(k.get("name", ""))[:28].ljust(30)
        fiy = str(k.get("price", 0)).rjust(5) + " TL"
        satir = f"{isim}{fiy}\n"
        fis += satir.encode("ascii", errors="replace")
        fis_text += satir
        
        notes = clean_tr(k.get("notes", ""))
        if notes:
            if notes.upper().startswith("NOT:"):
                fis += f"   {notes}\n".encode("ascii", errors="replace")
                fis_text += f"   {notes}\n"
            else:
                fis += f"   NOT: {notes}\n".encode("ascii", errors="replace")
                fis_text += f"   NOT: {notes}\n"

    fis += ALIGN_CENTER + SIZE_NORMAL + BOLD_OFF + b"------------------------------------------\n"
    fis += SIZE_DEV + BOLD_ON + f"TOPLAM: {total_amount},00\n".encode("ascii", errors="replace")
    fis += SIZE_NORMAL + BOLD_OFF + b"------------------------------------------\nAFIYET OLSUN\n\n\n\n\n\n"

    fis_text += "------------------------------------------\n"
    fis_text += f"TOPLAM: {total_amount},00\n"
    fis_text += "------------------------------------------\nAFIYET OLSUN\n"

    if "PDF" in yazici_adi.upper() or "XPS" in yazici_adi.upper():
        try:
            import win32ui
            import win32con
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(yazici_adi)
            hDC.StartDoc("Adisyon")
            hDC.StartPage()
            
            font_normal = win32ui.CreateFont({"name": "Courier New", "height": 40, "weight": 400})
            font_dev = win32ui.CreateFont({"name": "Courier New", "height": 70, "weight": 700})
            
            y = 100
            # Sayfa genişliğini yaklaşık 1000px kabul ediyoruz
            paper_width = 1000 
            
            def print_line(text, font, align="left"):
                nonlocal y
                hDC.SelectObject(font)
                width, height = hDC.GetTextExtent(text)
                if align == "center":
                    x = (paper_width - width) // 2
                else:
                    x = 100
                hDC.TextOut(x, y, text)
                y += height + 5

            print_line("SARACOGLU DONER", font_dev, "center")
            y += 30
            print_line(f"Tarih/Saat: {time}", font_normal)
            print_line(f"Masa: {customer_name}", font_normal)
            print_line("-" * 42, font_normal)
            
            for k in items:
                isim = clean_tr(k.get("name", ""))[:28].ljust(30)
                fiy = str(k.get("price", 0)).rjust(5) + " TL"
                print_line(f"{isim}{fiy}", font_normal)
                
                notes = clean_tr(k.get("notes", ""))
                if notes:
                    if not notes.upper().startswith("NOT:"):
                        notes = f"NOT: {notes}"
                    
                    # 42 karaktere göre kelime kaydirma (word wrap)
                    words = notes.split(" ")
                    wrapped_lines = []
                    current_line = "   "
                    for word in words:
                        if len(current_line) + len(word) + 1 > 42:
                            wrapped_lines.append(current_line)
                            current_line = "   " + word
                        else:
                            current_line += (" " if current_line != "   " else "") + word
                    if current_line.strip():
                        wrapped_lines.append(current_line)
                        
                    for wl in wrapped_lines:
                        print_line(wl, font_normal)
                        
            print_line("-" * 42, font_normal)
            y += 10
            print_line(f"TOPLAM: {total_amount},00 TL", font_dev, "center")
            y += 10
            print_line("-" * 42, font_normal)
            print_line("AFIYET OLSUN", font_normal, "center")
            
            hDC.EndPage()
            hDC.EndDoc()
            logger.info(f"Fis PDF/XPS olarak yazdirildi: Masa {customer_name}")
        except Exception as e:
            logger.error(f"PDF/XPS Yazdirma hatasi: {e}")
        return

    try:
        hPrinter = win32print.OpenPrinter(yazici_adi)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Adisyon", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, bytes(fis))
            win32print.WritePrinter(hPrinter, CUT)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            logger.info(f"Fis basariyla yazdirildi: Masa {customer_name}")
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        logger.error(f"Yazdirma hatasi: {e}\n{traceback.format_exc()}")

def get_available_printers():
    if not YAZICI_AKTIF:
        return []
    try:
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        return printers
    except Exception as e:
        logger.error(f"Yazici listesi alinirken hata: {e}")
        return []
