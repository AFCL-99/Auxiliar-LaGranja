from datetime import datetime
import os
from reportlab.lib.utils import ImageReader
import unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, LETTER
from PIL import Image, ImageEnhance
import sys

from PyPDF2 import PdfMerger
import webbrowser

from app.core.pagos import FLETES, NOMINA, PROVEEDORES
from app.utils.OCR import extraer_datos_banco

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

CARPETA_SALIDA = "app/data/pdf_generados"
CARPETA_IMAGENES = "app/data/pagos a procesar"
SALIDA_PDF = "app/data/imprimir.pdf"
RECORTE_SUPERIOR = 0.04
ALTURA_CM = 18
RECORTE_INFERIOR = 0.04


def limpiar_texto(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    return texto.upper().strip()


def generar_nombre_y_carpeta(ruta_imagen):
    ruta_RP = ""
    nombre_base = os.path.splitext(os.path.basename(ruta_imagen))[0]

    recibo, fecha, nombre_detectado, valor, banco = extraer_datos_banco(ruta_imagen)
    if not fecha:
        print("No se detectó fecha en", nombre_base)
        fecha_str = datetime.now().strftime("%d-%m-%Y")
    else:
        fecha_str = fecha.strftime("%d-%m-%Y")
    tipo_carpeta, nombre_pdf = clasificar(nombre_detectado)
    tercero = nombre_pdf

    # PROVEEDORES
    if tipo_carpeta == "proveedores":
        factura = "PENDIENTE"
        nombre_pdf = f"{nombre_pdf} PG FC {factura} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "proveedores")

    # FLETES
    elif tipo_carpeta == "fletes":
        nombre_pdf = f"{nombre_pdf} {fecha_str} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "fletes")
        # ruta_RP = crear_flete_pago(tercero, valor, fecha, recibo, banco)
    # NOMINA
    elif tipo_carpeta == "nomina":
        if fecha:
            mes = fecha.strftime("%b").upper()
            año = fecha.strftime("%y")
            quincena = "Q1" if fecha.day <= 15 else "Q2"

        nombre_pdf = f"{quincena} {mes}{año} {nombre_pdf}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "nomina")

    elif tipo_carpeta == "otros":
        print("Pago desconocido: " + nombre_pdf)
        nombre_pdf = f"{nombre_pdf} {fecha_str} RCBO{recibo}.pdf"
        carpeta = os.path.join(CARPETA_SALIDA, "desconocido")
    else:
        return None, None, None
    print(tercero)
    return nombre_pdf, carpeta, ruta_RP


def clasificar(nombre):
    nombre = limpiar_texto(nombre)

    if nombre in PROVEEDORES:
        return "proveedores", PROVEEDORES[nombre]

    if nombre in FLETES:
        return "fletes", FLETES[nombre]

    if nombre in NOMINA:
        return "nomina", NOMINA[nombre]

    return "otros", nombre


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

    c.drawImage(imagen_path, 0, height - new_height, width=new_width, height=new_height)

    c.save()

    print("Guardado en:", ruta_pdf)


def procesar_imagen(ruta):
    img = Image.open(ruta)
    ancho, alto = img.size

    top = int(alto * RECORTE_SUPERIOR)
    bottom = int(alto * (1 - RECORTE_INFERIOR))

    img_recortada = img.crop((0, top, ancho, bottom))

    contraste = ImageEnhance.Contrast(img_recortada)
    img_recortada = contraste.enhance(0.9)

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
    x_centro = ancho_pagina / 2
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


def procesar_todas():
    generar_pdf()
    rutas_pdfs = []
    for archivo in os.listdir(CARPETA_IMAGENES):

        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):

            ruta = os.path.join(CARPETA_IMAGENES, archivo)

            nombre_pdf, carpeta, ruta_RP = generar_nombre_y_carpeta(ruta)
            if ruta_RP != "":
                rutas_pdfs.append(ruta_RP)
            if nombre_pdf and carpeta:
                crear_pdf(ruta, nombre_pdf, carpeta)
    unir_pdfs(rutas_pdfs, "RP.pdf")
    return ""


def unir_pdfs(rutas, salida):

    merger = PdfMerger()

    for pdf in rutas:
        merger.append(pdf)

    merger.write(salida)

    merger.close()


procesar_todas()
