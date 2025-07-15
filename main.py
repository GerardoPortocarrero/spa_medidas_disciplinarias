# Importaciones estándar
import subprocess
import sys
import threading
import time
import locale
import webbrowser

# Importaciones de dependencias externas
from flask import Flask, Response, send_from_directory
import pandas as pd
import msoffcrypto
from io import BytesIO

# Constantes
REQUIREMENTS = ["flask", "pandas", "openpyxl", "msoffcrypto-tool"]
EXCEL = "MEDIDAS DISCIPLINARIAS OFICIAL.xlsx"
PASSWORD = "aya204983"

# Configuración inicial
def setup_locale():
    """Configura el locale en español para formato de fechas."""
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")  # Linux/Mac
    except:
        try:
            locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")  # Windows
        except:
            pass  # Si no funciona, usa el locale por defecto

def install_missing_packages():
    """Instala los paquetes necesarios si no están presentes."""
    for package in REQUIREMENTS:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def open_browser():
    """Abre el navegador en localhost después de un retraso."""
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

# Configuración de la aplicación Flask
app = Flask(__name__)

@app.route("/")
def index():
    """Sirve la página principal (index.html) desde la carpeta static."""
    return send_from_directory("static", "index.html")

@app.route("/file.csv")
def serve_csv():
    """Procesa el archivo Excel, formatea fechas, elimina columnas específicas y devuelve un CSV."""
    # Desencriptar el archivo Excel
    decrypted = BytesIO()
    with open(EXCEL, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=PASSWORD)
        office_file.decrypt(decrypted)
    decrypted.seek(0)

    # Leer el archivo Excel y limpiar columnas
    df = pd.read_excel(decrypted, engine="openpyxl", header=0)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]  # Eliminar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains("NUMERO", case=False)]    # Eliminar columnas con "NUMERO" en el nombre

    # Formatear columnas de fecha al formato '02 enero 2025'
    for col in df.columns:
        if "FECHA" in col.upper():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].dt.strftime("%d %B %Y").str.lower()
            except Exception as e:
                print(f"Error al formatear la columna {col}: {e}")

    # Convertir a CSV en memoria con codificación UTF-8
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, sep=";", index=False, encoding="utf-8-sig")  # Usar utf-8-sig para BOM
    csv_buffer.seek(0)

    # Devolver respuesta con encabezado explícito de UTF-8
    return Response(
        csv_buffer.read(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=sanciones.csv"}
    )

# Ejecución principal
if __name__ == "__main__":
    # Configurar dependencias y locale
    install_missing_packages()
    setup_locale()
    
    # Iniciar el navegador en un hilo separado
    threading.Thread(target=open_browser).start()
    
    # Iniciar la aplicación Flask con recarga automática
    app.run(debug=True, port=8000)