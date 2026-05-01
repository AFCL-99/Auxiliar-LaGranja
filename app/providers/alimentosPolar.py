import re

def es_numero(x):
    return re.match(r"^\d+(\.\d+)?$", x)

def limpiar_numero(texto):
    return texto.replace(".", "").replace(",", ".")

def procesar(texto):
    lineas = texto.split("\n")
    items = []

    for linea in lineas:
        linea = linea.strip()

        # 🔥 detectar línea de producto (empieza con código tipo m1103)
        if not re.match(r"^[a-zA-Z]\d{3,}", linea):
            continue

        try:
            limpia = (
                linea.replace("$", "")
                .replace(".", "")
                .replace(",", ".")
            )

            partes = limpia.split()

            codigo = partes[0]

            # 🔥 extraer solo números
            numeros = [float(p) for p in partes if es_numero(p)]

            if len(numeros) < 8:
                raise ValueError("No hay suficientes números")

            # 🔥 mapeo desde la derecha
            cantidad = numeros[-9]
            precio_unitario = numeros[-6]
            descuento = numeros[-4]
            iva = numeros[-2]/100

            items.append({
                "codigo": codigo,
                "cantidad": cantidad,
                "precio": precio_unitario,
                "descuento": descuento,
                "iva": iva
            })

        except Exception as e:
            print(f"Error procesando línea: {linea}", e)

    factura_id = extraer_factura(texto)
    return {
        "proveedor": "ALIMENTOS POLAR",
        "factura_id": factura_id,
        "items": items
    }

def extraer_factura(texto):
    match = re.search(r"nica de venta no.ffnz\s*(\d+)", texto)
    if match:
        return f"FFNZ-{match.group(1)}"

    return "SIN_ID"