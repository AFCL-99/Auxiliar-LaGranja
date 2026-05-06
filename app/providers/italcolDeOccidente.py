import re

def es_numero(valor):
    try:
        float(valor)
        return True
    except:
        return False


def limpiar_numero(valor):
    return float(
        valor.replace("$", "")
             .replace(".", "")
             .replace(",", ".")
             .strip()
    )


def extraer_factura_italcol(texto):
    """
    Busca un consecutivo tipo 115m33085
    y devuelve prefijo 115M y número 33085
    """
    match = re.search(r"\b(\d{3}[a-zA-Z])\s*-?\s*(\d{4,})\b", texto)

    if not match:
        return {
            "prefijo": None,
            "numero": None,
            "factura_id": None
        }

    prefijo = match.group(1).upper()
    numero = match.group(2)

    return {
        "prefijo": prefijo,
        "numero": numero,
        "factura_id": f"{prefijo}-{numero}"
    }


def procesar(texto):
    lineas = texto.split("\n")
    items = []

    for linea in lineas:
        linea = linea.strip().lower()

        # Detecta producto: empieza con código numérico de 5 o más dígitos
        if not re.match(r"^\d{5,}\s+", linea):
            continue

        try:
            # Ejemplo:
            # 154506 agility gatos pack(3*3kg) lote:1304-9432 2 pac 18 $160.727 $ 321.454 5 %

            codigo = linea.split()[0]

            patron = re.search(
                r"^(\d{5,})\s+.*?\s+"
                r"(\d+(?:[.,]\d+)?)\s+"      # cantidad
                r"([a-zA-Z]+)\s+"            # unidad
                r"(\d+(?:[.,]\d+)?)\s+"      # kilos
                r"\$?\s*([\d.,]+)\s+"        # precio unitario
                r"\$?\s*([\d.,]+)\s+"        # subtotal
                r"(\d+(?:[.,]\d+)?)\s*%?",   # IVA
                linea
            )

            if not patron:
                raise ValueError("No se pudo interpretar la línea del producto")

            cantidad = limpiar_numero(patron.group(2))
            precio_unitario = limpiar_numero(patron.group(5))
            iva = limpiar_numero(patron.group(7))

            cantidad = limpiar_numero(patron.group(2))
            precio_unitario = limpiar_numero(patron.group(5))
            iva = limpiar_numero(patron.group(7)) 

            descuento = round(precio_unitario * cantidad * 0.02, 2)

            items.append({
                "codigo": codigo,
                "cantidad": cantidad,
                "precio": precio_unitario,
                "descuento": descuento,
                "iva": iva
            })

        except Exception as e:
            print(f"Error procesando línea: {linea}", e)

    factura = extraer_factura_italcol(texto)

    return {
        "proveedor": "ITALCOL DE OCCIDENTE SA",
        "factura_id": factura["factura_id"],
        "items": items
    }
