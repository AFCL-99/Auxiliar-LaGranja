import re

def es_numero(x):
    return re.match(r"^\d+(\.\d+)?$", x)

def procesar(texto):
    texto = cortar_primera_pagina(texto)
    lineas = texto.split("\n")
    items = []

    en_items = False

    for linea in lineas:
        linea = linea.strip()

        if re.search(r"codigo|descripcion|cant|precio", linea.lower()):
            en_items = True
            continue

        if re.search(r"total kilos total bruto", linea.lower()):
            break

        if not en_items:
            continue

        if not re.match(r"^\d{3,}", linea):
            continue

        try:
            limpia = (
                linea.replace("$", "")
                .replace(".", "")
                .replace(",", ".")
            )

            partes = limpia.split()
            codigo = partes[0]

            # 🔥 tomar solo números válidos
            numeros = [float(p) for p in partes if es_numero(p)]

            if len(numeros) < 5:
                raise ValueError("No hay suficientes números")

            # 🔥 leer desde atrás (más confiable)
            total = numeros[-1]
            iva = numeros[-2]
            valor_iva = numeros[-3]
            subtotal = numeros[-4]
            precio_unitario = numeros[-5]

            cantidad = numeros[-7] if len(numeros) >= 7 else numeros[0]

            items.append({
                "codigo": codigo,
                "cantidad": cantidad,
                "precio": precio_unitario,
                "descuento": 0,
                "iva": iva
            })

        except Exception as e:
            print(f"Error procesando línea ITALCOL: {linea}", e)

    factura_id = extraer_factura(texto)

    return {
        "proveedor": "ITALCOL",
        "factura_id": factura_id,
        "items": items
    }
def extraer_factura(texto):
    match = re.search(r"factura electronica de venta pame\s*(\d+)", texto)
    if match:
        return f"PAME-{match.group(1)}"

    return "SIN_ID"

def cortar_primera_pagina(texto):

    # patrón flexible
    patron = r"elaborado por:.*?original"

    match = re.search(patron, texto, re.IGNORECASE)

    if match:
        return texto[:match.end()]

    return texto