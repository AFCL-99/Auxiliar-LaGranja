import os
import cv2
import re
from reportlab.lib.utils import ImageReader
from datetime import datetime
import unicodedata
import easyocr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, LETTER
from PIL import Image, ImageEnhance
import sys
import webbrowser

sys.stdout.reconfigure(encoding='utf-8') # type: ignore

CARPETA_SALIDA = "app/images/pdf_generados"
CARPETA_IMAGENES ="app/images/pagosAProcesar"
SALIDA_PDF = "app/images/imprimir.pdf"
RECORTE_SUPERIOR = 0.04
ALTURA_CM = 18
RECORTE_INFERIOR = 0.04

reader = easyocr.Reader(['es'], gpu=True)
PROVEEDORES = {
    "LAURA GABRIELA OSORIO VALDERRAMA":"GABRIELA VALDERRAMA",
    "OSCAR DANIEL LOMBANA LOPEZ": "BARFIT",
    "AGROSOLLA SAS": "AGROSOLLA SAS",
    "COLOMBOSALES": "COLOMBOSALES SAS",
    "LABORATORIOS LAVERLA": "LABORATORIOS LAVERLAM SA",
    "DISPROVET COLOMBIA SAS": "DISPROVET COLOMBIA SAS",
    "ENERVIDA SAS": "ENERVIDA SAS",
    "TELEVIGILANCIA LTDA": "TELEVIGILANCIA LTDA",
    "OLVER ANTURY CARVAJAL": "OLVER ANTURY CARVAJAL",
    "PROANDINA": "SIERRA PINEDA",
    "LA CASA DEL GANADERO": "LA CASA DEL GANADERO",
    "CENTRAL PECUARIA SA": "CENTRAL PECUARIA S.A.",
    "LAB EDO SAS": "LABORATORIOS EDO SAS",
    "ALIMENTOS POLAR SAS": "ALIMENTOS POLAR",
    "GABRICA SAS": "GABRICA SAS",
    "INVERCIONES AGROCOSUR": "INVERSIONES AGROCOSUR",
    "TAMAYO POLANCO SAS": "TAMAYO POLANCO"
}

FLETES = {
    "ESNEDA H": "ESNEDA HERNANDEZ",
    "BRAYAN GARCIA":"BRAYAN ROLDAN GARCIA",
    "JUAN CARLOS":"JUAN CARLOS ROJAS"
}

NOMINA = {
    "ANDRES CORTEZ": "ANDRES CORTEZ",
    "JULIAN LOPEZ": "JULIAN LOPEZ",
    "EDUARDO SANCHEZ":"EDUARDO SANCHEZ",
    "LUISA LOPEZ": "LUISA MARIA",
    "CARLOS OLAYA": "CARLOS OLAYA",
    "JUAN CAMILO CASTILLO": "CAMILO CASTILLO",
    "ANDRES FELIPE CLAROS": "ANDRES CLAROS",
    "JOHN FREDDY MAPALLO GAVIRIA": "JHON MAPAYO",
    "KAREN YURLEI MAPALLO BOLA": "KAREN MAPAYO",
    "HEINERT ZU": "HEINERT ZUÑIGA",
    "EDGAR ANDRES POLANCO": "EDGAR POLANCO",
    "DUVAN ANDRES GUZMAN CRUZ": "DUVAN ANDRES",
    "WILMER NICOLAS BRAVO": "NICOLAS BRAVO",
    "BRAYHAN RODRIGUEZ": "STIVEN RODRIGUEZ"
}

def limpiar_texto(texto):
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto.upper().strip()
def extraer_nombre(texto):

    texto = texto.lower()

    # 🔥 buscar después de "producto destino"
    match = re.search(r"producto destino\s+([a-z\s]+)", texto)

    if match:
        nombre = match.group(1).strip()

        # limpiar basura
        nombre = nombre.split("corriente")[0]

        nombre = nombre.split("ahorros")[0]
        nombre = nombre.split("\n")[0]

        return nombre.upper()

    # 🔥 fallback (por si cambia formato)
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

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) # type: ignore 
    _, binaria = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY)

    resultados = reader.readtext(binaria)
    texto = " ".join([r[1] for r in resultados]).lower() # type: ignore
    # Detectar banco
    banco = "bancolombia" if "transferencia exitosa" in texto else "davivienda"

    # RECIBO
    match_recibo = re.search(r'\b\d{6,10}\b', texto)
    recibo = None

    if match_recibo:
        numero = match_recibo.group()
        if banco == "bancolombia":
            recibo = numero[-4:]
        else:
            recibo = numero.lstrip("0")

    # FECHA
    fecha = None

    match_fecha1 = re.search(r'\d{2}/\d{2}/\d{4}', texto)
    if match_fecha1:
        fecha = datetime.strptime(match_fecha1.group(), "%d/%m/%Y")

    else:
        match_fecha2 = re.search(r'\d{1,2}\s+[a-zA-Z]{3}\s+\d{4}', texto)
        if match_fecha2:
            fecha_str = match_fecha2.group().lower()

            meses = {
                'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
                'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
                'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
            }

            for es, en in meses.items():
                fecha_str = fecha_str.replace(es, en)

            fecha = datetime.strptime(fecha_str, "%d %b %Y")
    
    texto_completo = " ".join([r[1] for r in resultados]).lower()  # type: ignore

    nombre = extraer_nombre(texto_completo)
    return recibo, fecha, nombre

def generar_nombre_y_carpeta(ruta_imagen):

    nombre_base = os.path.splitext(os.path.basename(ruta_imagen))[0]

    recibo, fecha, nombre_detectado = extraer_datos_banco(ruta_imagen)
    if not fecha:
        print("No se detectó fecha en", nombre_base)
        fecha_str = datetime.now().strftime("%d-%m-%Y")
    else:
        fecha_str = fecha.strftime("%d-%m-%Y")
    tipo_carpeta, nombre_pdf = clasificar(nombre_detectado)
    # PROVEEDORES
    if tipo_carpeta == "proveedores":
        factura = "PENDIENTE"
        nombre_pdf = f"{nombre_pdf} PG FC {factura} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "proveedores")

    # FLETES
    elif tipo_carpeta == "fletes":
        nombre_pdf = f"{nombre_pdf} {fecha_str} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "fletes")

    # NOMINA
    elif tipo_carpeta == "nomina":
        mes = fecha.strftime("%b").upper()
        año = fecha.strftime("%y")
        quincena = "Q1" if fecha.day <= 15 else "Q2"

        nombre_pdf = f"{quincena} {mes}{año} {nombre_pdf}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "nomina")

    elif tipo_carpeta == "otros":
        print("Pago desconocido: "+nombre_pdf)
        nombre_pdf = f"{nombre_pdf} {fecha_str} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "desconocido")
    else:
        return None, None

    return nombre_pdf, carpeta

def clasificar(nombre):
    nombre = limpiar_texto(nombre)

    if nombre in PROVEEDORES:
        return "proveedores",PROVEEDORES[nombre]

    if nombre in FLETES:
        return "fletes",FLETES[nombre]

    if nombre in NOMINA:
        return "nomina",NOMINA[nombre]

    return "otros",nombre

def crear_pdf(imagen_path, nombre_pdf, carpeta_destino):

    os.makedirs(carpeta_destino, exist_ok=True)
    ruta_pdf = os.path.join(carpeta_destino, nombre_pdf)

    c = canvas.Canvas(ruta_pdf, pagesize=LETTER)
    width, height = LETTER

    img = Image.open(imagen_path)
    img_width, img_height = img.size

    ratio = min(width / img_width, height / img_height)
    new_width = img_width * ratio
    new_height = img_height * ratio

    c.drawImage(imagen_path, 0, height - new_height,
                width=new_width, height=new_height)

    c.save()

    print("Guardado en:", ruta_pdf)

def procesar_todas():
    #generar_pdf()
    for archivo in os.listdir(CARPETA_IMAGENES):

        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):

            ruta = os.path.join(CARPETA_IMAGENES, archivo)

            nombre_pdf, carpeta = generar_nombre_y_carpeta(ruta)
            if nombre_pdf and carpeta:
                crear_pdf(ruta, nombre_pdf, carpeta)
    return ""

def procesar_imagen(ruta):
    img = Image.open(ruta)
    ancho, alto = img.size

    top = int(alto * RECORTE_SUPERIOR)
    bottom = int(alto * (1 - RECORTE_INFERIOR))

    img_recortada = img.crop((0, top, ancho, bottom))

    # reducir contraste ligeramente
    contraste = ImageEnhance.Contrast(img_recortada)
    img_recortada = contraste.enhance(0.9)

    # reducir color ligeramente
    color = ImageEnhance.Color(img_recortada)
    img_recortada = color.enhance(0.9)

    return img_recortada

def cm_a_puntos(cm):
    return cm * 72 / 2.54
def obtener_imagenes(carpeta):
    archivos = sorted(os.listdir(carpeta))
    return [
        os.path.join(carpeta, f)
        for f in archivos
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def agregar_imagen(c, img, x_centro, y_centro):
    alto_pagina, ancho_pagina = LETTER
    altura_final = cm_a_puntos(ALTURA_CM)

    ancho_px, alto_px = img.size
    ratio = altura_final / alto_px

    nuevo_ancho = ancho_px * ratio
    nuevo_alto = altura_final

    x = x_centro - (nuevo_ancho / 2)
    y = y_centro - (nuevo_alto / 2)

    img_reader = ImageReader(img)
    c.drawImage(img_reader, x, y, width=nuevo_ancho, height=nuevo_alto)
    c.setLineWidth(0.5)
    largo_marca = 10
    x_centro = ancho_pagina/2
    # marca superior
    c.line(x_centro, alto_pagina, x_centro, alto_pagina - largo_marca)

    # marca inferior
    c.line(x_centro, 0, x_centro, largo_marca)


def generar_pdf():
    c = canvas.Canvas(SALIDA_PDF, pagesize=landscape(LETTER))
    ancho_pagina, alto_pagina = landscape(LETTER)

    imagenes = obtener_imagenes(CARPETA_IMAGENES)

    for i in range(0, len(imagenes), 2):
        mitad_ancho = ancho_pagina / 2

        img1 = procesar_imagen(imagenes[i])
        agregar_imagen(
            c,
            img1,
            x_centro=mitad_ancho / 2,
            y_centro=alto_pagina / 2,
        )

        if i + 1 < len(imagenes):
            img2 = procesar_imagen(imagenes[i + 1])
            agregar_imagen(
                c,
                img2,
                x_centro=mitad_ancho + (mitad_ancho / 2),
                y_centro=alto_pagina / 2,
            )

        c.showPage()

    c.save()
    print("PDF generado correctamente:", SALIDA_PDF)
    ruta = os.path.abspath(SALIDA_PDF)
    webbrowser.open(f"file:///{ruta}")

procesar_todas()