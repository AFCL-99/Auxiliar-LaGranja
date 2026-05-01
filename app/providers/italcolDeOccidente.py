import math
import re

def limpiar_numero(valor):
    valor = valor.replace("$", "").replace(",", "").strip()
    return float(valor) if valor else 0.0


def extraer_factura(texto: str):

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    if len(lineas) >= 3:
        return lineas[2]  # 👈 tercera línea

    return None

import re

def procesar_factura_italcol(texto: str):

    items = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for linea in lineas:

        if not re.match(r"^\d{4,6}\s", linea):
            continue

        try:
            partes = linea.split()

            codigo = partes[0]
            print(codigo)
            # 🔹 encontrar IVA (última posición tipo 5 %)
            iva = None
            for i, p in enumerate(partes):
                if "%" in p:
                    iva = float(p.replace("%", "").strip())
                    idx_iva = i
                    break

            # 🔹 valor unitario (antes del $)
            valores = [p for p in partes if "$" in p]

            valor_unitario = float(
                valores[0].replace("$", "").replace(".", "").replace(",", ".")
            )

            cantidad = float(partes[2])

            # 🔹 descripción (todo entre código y cantidad)
            descripcion = " ".join(partes[1:2])  # base mínima

            # 🔥 mejor extracción de descripción
            descripcion = extraer_descripcion(linea)

            # 🔥 transformar cantidades
            cantidad_real, precio_real = transformar_unidades(
                descripcion, cantidad, valor_unitario
            )

            items.append({
                "code": codigo,
                "description": descripcion,
                "quantity": cantidad_real,
                "price": precio_real,
                "iva": iva
            })

        except Exception as e:
            print("Error procesando línea:", linea, e)

    return items

def procesar(texto):
    items = []

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    for linea in lineas:
        if not re.match(r"^\d{4,6}\s", linea):
            continue

        try:
            partes = linea.split()

            codigo = partes[0]
            print(codigo)

        except Exception as e:
            print("Error procesando línea:", linea, e)