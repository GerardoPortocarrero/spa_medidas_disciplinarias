import msoffcrypto
import pandas as pd
from io import BytesIO
from flask import Flask, Response, send_from_directory
import locale

# Intentar establecer el locale en español para nombres de mes
try:
    locale.setlocale(locale.LC_TIME, "es_ES.utf8")  # Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")  # Windows
    except:
        pass  # Si falla, sigue con el default (en inglés)

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

    # Leer Excel con encabezado real
    xls = pd.ExcelFile(decrypted, engine="openpyxl")
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=0)

    # Limpiar columnas sin nombre como 'Unnamed: ...'
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # Detectar y formatear columnas de fecha
    for col in df.columns:
        if "FECHA" in col.upper():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].dt.strftime("%d %B %Y").str.title()
            except Exception as e:
                print(f"Error al convertir la columna {col}: {e}")

    # Convertir a CSV en memoria
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, sep=";", index=False)
    csv_buffer.seek(0)

    return Response(csv_buffer.read(), mimetype="text/csv")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
