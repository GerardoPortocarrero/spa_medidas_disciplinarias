import locale
import time
import webbrowser
import pandas as pd
import msoffcrypto
from io import BytesIO
from .config import EXCEL, PASSWORD, PORT

def setup_locale():
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")
    except:
        try:
            locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")
        except:
            pass

def open_browser():
    time.sleep(2)
    webbrowser.open(f"http://localhost:{PORT}")

def procesar_excel():
    decrypted = BytesIO()
    with open(EXCEL, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=PASSWORD)
        office_file.decrypt(decrypted)
    decrypted.seek(0)

    df = pd.read_excel(decrypted, engine="openpyxl", header=0)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]
    df = df.loc[:, ~df.columns.str.contains("NUMERO", case=False)]

    for col in df.columns:
        if "FECHA" in col.upper():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].dt.strftime("%d %B %Y").str.lower()
            except Exception as e:
                print(f"Error en columna {col}: {e}")

    return df.to_csv(index=False, sep=";", encoding="utf-8-sig")
