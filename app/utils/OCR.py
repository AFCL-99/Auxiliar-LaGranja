from csv import reader
from datetime import datetime
import cv2
import easyocr
import re

reader = easyocr.Reader(["es"], gpu=True)


def extraer_valor(texto):
    match = re.search(r"valor[\s\$]*([\d\.\,]+)", texto, re.IGNORECASE)

    if not match:
        match = re.search(r"transferencia[\s\$]*([\d\.\,]+)", texto, re.IGNORECASE)
    else:
        valor_str = match.group(1)

        valor_str = valor_str.replace(".", "").replace(",", ".")

        try:
            valor = float(valor_str)
            if valor >= 51000000:
                valor = valor - 50000000
            return valor
        except Exception:
            return 0


def extraer_nombre(texto):

    texto = texto.lower()

    match = re.search(r"producto destino\s+([a-z\s]+)", texto)

    if match:
        nombre = match.group(1).strip()

        # limpiar basura
        nombre = nombre.split("corriente")[0]

        nombre = nombre.split("ahorros")[0]
        nombre = nombre.split("\n")[0]

        return nombre.upper()

    lineas = texto.split("\n")

    for i, linea in enumerate(lineas):
        if "producto destino" in linea:
            if i + 1 < len(lineas):
                return lineas[i + 1].strip().upper()

    match = re.search(r"destino\s+([a-z\s]+)", texto)
    if match:
        nombre = match.group(1).strip()
        return nombre.upper()
    return "NOMBRE_NO_DETECTADO"


def extraer_datos_banco(ruta_imagen):

    imagen = cv2.imread(ruta_imagen)

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)  # type: ignore
    _, binaria = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY)

    resultados = reader.readtext(binaria)
    texto = " ".join([r[1] for r in resultados]).lower()  # type: ignore

    banco = "bancolombia" if "datos de la transferencia" in texto else "davivienda"

    # RECIBO
    match_recibo = re.search(r"\b\d{6,10}\b", texto)
    recibo = None

    if match_recibo:
        numero = match_recibo.group()
        if banco == "bancolombia":
            recibo = numero[-4:]
        else:
            recibo = numero.lstrip("0")

    # FECHA
    fecha = None

    match_fecha1 = re.search(r"\d{2}/\d{2}/\d{4}", texto)
    if match_fecha1:
        fecha = datetime.strptime(match_fecha1.group(), "%d/%m/%Y")

    else:
        match_fecha2 = re.search(r"\d{1,2}\s+[a-zA-Z]{3}\s+\d{4}", texto)
        if match_fecha2:
            fecha_str = match_fecha2.group().lower()

            meses = {
                "ene": "Jan",
                "feb": "Feb",
                "mar": "Mar",
                "abr": "Apr",
                "may": "May",
                "jun": "Jun",
                "jul": "Jul",
                "ago": "Aug",
                "sep": "Sep",
                "oct": "Oct",
                "nov": "Nov",
                "dic": "Dec",
            }

            for es, en in meses.items():
                fecha_str = fecha_str.replace(es, en)

            fecha = datetime.strptime(fecha_str, "%d %b %Y")

    texto_completo = " ".join([r[1] for r in resultados]).lower()  # type: ignore

    nombre = extraer_nombre(texto_completo)
    valor = extraer_valor(texto_completo)

    return recibo, fecha, nombre, valor, banco
