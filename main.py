import subprocess
import sys
import webbrowser
import threading
import time
import locale

# Módulos necesarios
REQUIREMENTS = ["flask", "pandas", "openpyxl", "msoffcrypto-tool"]

def install_missing_packages():
    for package in REQUIREMENTS:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

# Instalar dependencias si faltan
install_missing_packages()
threading.Thread(target=open_browser).start()

from flask import Flask, Response, send_from_directory
import pandas as pd
import msoffcrypto
from io import BytesIO

# Intentar establecer locale en español
try:
    locale.setlocale(locale.LC_TIME, "es_ES.utf8")  # Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")  # Windows
    except:
        pass  # Si no funciona, seguirá en inglés

app = Flask(__name__)
EXCEL = "MEDIDAS DISCIPLINARIAS OFICIAL.xlsx"
PASSWORD = "aya204983"

@app.route("/file.csv")
def serve_csv():
    decrypted = BytesIO()
    with open(EXCEL, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=PASSWORD)
        office_file.decrypt(decrypted)
    decrypted.seek(0)

    df = pd.read_excel(decrypted, engine="openpyxl", header=0)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # Convertir columnas de fecha al formato '02 enero 2025'
    for col in df.columns:
        if "FECHA" in col.upper():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].dt.strftime("%d %B %Y").str.lower()
            except Exception as e:
                print(f"Error al formatear la columna {col}: {e}")

    # Convertir a CSV en memoria
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, sep=";", index=False)
    csv_buffer.seek(0)
    return Response(csv_buffer.read(), mimetype="text/csv")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=False, port=8000)
