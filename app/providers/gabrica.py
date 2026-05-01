import re

def es_numero(x):
    return re.match(r"^\d+(\.\d+)?$", x)

def limpiar_numero(texto):
    return texto.replace(".", "").replace(",", ".")

def procesar(texto):

    lineas = texto.split("\n")
    lineas = [l.strip() for l in lineas if l.strip()]

    items = []
    buffer = ""

    def es_inicio_producto(linea):
        # ejemplo: 10 11001025 ...
        return re.match(r'^\d+\s+\d{6,}', linea)

    # 🔹 1. recorrer líneas y agrupar bloques
    for linea in lineas:

        # saltar ruido
        if "cufe:" in linea.lower():
            continue

        if "tipo de operación" in linea.lower():
            continue

        if es_inicio_producto(linea):

            if buffer:
                item = parsear_item(buffer)
                if item:
                    items.append(item)

            buffer = linea

        else:
            # línea adicional (nombre, kg, etc)
            buffer += " " + linea

    # último item
    if buffer:
        item = parsear_item(buffer)
        if item:
            items.append(item)

    return {
        "items": items,
        "proveedor": "GABRICA",
        "factura_id": extraer_factura(texto)
    }

def extraer_factura(texto):
    match = re.search(r"mero: bog\s*(\d+)", texto)
    if match:
        return f"BOG-{match.group(1)}"

    return "SIN_ID"

def parsear_item(texto):

    try:
        # 🔹 código
        codigo = re.search(r'\d+\s+(\d{6,})', texto).group(1)

        # 🔹 cantidad
        cantidad = float(re.search(r'(\d+\.\d{2})\s+94', texto).group(1))

        # 🔹 precio unitario
        precio = re.search(r'\$\s*([\d,]+\.\d{2})', texto)
        precio = float(precio.group(1).replace(",", ""))

        # 🔹 descuento
        descuentos = re.findall(r'\$\s*([\d,]+\.\d{2})', texto)
        descuento = float(descuentos[1].replace(",", "")) if len(descuentos) > 1 else 0

        # 🔹 iva %
        iva = int(re.search(r'(\d+)%', texto).group(1))

        # 🔹 descripción limpia (todo lo que no sea números clave)
        descripcion = limpiar_descripcion(texto, codigo)
        cantidad, precio = transformar_pacas(codigo, cantidad, precio)
        return {
            "codigo": codigo,
            "description": descripcion,
            "cantidad": cantidad,
            "precio": formatear_precio(precio),
            "descuento": descuento,
            "iva": iva
        }

    except Exception:
        return None
    

def limpiar_descripcion(texto, codigo):

    # quitar todo lo estructural
    texto = re.sub(r'^\d+\s+' + codigo, '', texto)

    texto = re.sub(r'\$\s*[\d,]+\.\d{2}', '', texto)
    texto = re.sub(r'\d+\.\d{2}', '', texto)
    texto = re.sub(r'\d+%', '', texto)
    texto = re.sub(r'\b94\b', '', texto)

    return texto.strip()

CONVERSIONES = {
    "15402011": 30,
    "11203011": 2,
    "11203010": 2,
    "11203009": 3
}
def transformar_pacas(codigo, cantidad, precioUnitario):
    unidades_por_paca = CONVERSIONES.get(codigo,1)
    unidades = cantidad * unidades_por_paca
    valor_total = cantidad * precioUnitario
    precio_real = valor_total/unidades if unidades else 0

    return unidades, precio_real

from decimal import Decimal, ROUND_HALF_UP

def formatear_precio(valor):
    return float(
        Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )