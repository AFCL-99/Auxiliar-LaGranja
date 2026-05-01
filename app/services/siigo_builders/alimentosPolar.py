def separar_factura_id(factura_id):
    prefijo, numero = factura_id.split("-")
    return prefijo, numero

def calcular_total(items):
    total = 0

    for item in items:
        cantidad = item["cantidad"]
        precio = item["precio"]
        descuento = item.get("descuento", 0)

        descuento_unitario = descuento / cantidad if cantidad else 0
        precio_final = round(precio - descuento_unitario, 2)

        base = round(precio_final * cantidad, 2)

        iva_porcentaje = item.get("iva", 0)
        iva = round(base * iva_porcentaje / 100, 2)

        total += base + iva

    return round(total, 2)

TAX_MAP = {
    5: 7316,
    19: 7315
}
BODEGA_PLANTAS_NEIVA = 73
BODEGA_PRINCIPAL = 69

def mapear_items_siigo(items):
    items_siigo = []

    for item in items:
        tax_id = TAX_MAP.get(item.get("iva"))

        items_siigo.append({
            "type": "Product",
            "code": str(item["codigo_siigo"]),
            "quantity": item["cantidad"],
            "price": item["precio"],
            "discount": item.get("descuento", 0),
            "warehouse": BODEGA_PRINCIPAL,
            "taxes": [{"id": tax_id}] if tax_id else []
        })

    return items_siigo

DOCUMENT_ID = 14148
COST_CENTER = 367

SUPPLIER = {
    "id": "a1a0fc32-152d-4b77-b4e1-bce0e155aa5c",
    "identification": "830006735",
    "branch_office": 0
}

PAYMENT_ID = 4390


def construir(data):

    factura_id = data["factura_id"]
    items = data["items"]
    fecha = data["fecha"]

    prefijo, numero = separar_factura_id(factura_id)

    items_siigo = mapear_items_siigo(items)

    total = calcular_total(items)

    payload = {
        "document": {
            "id": DOCUMENT_ID
        },
        "date": fecha,
        "cost_center": COST_CENTER,
        "supplier": SUPPLIER,
        "provider_invoice": {
            "prefix": prefijo,
            "number": numero
        },
        "discount_type": "Percentage",
        "items": items_siigo,
        "payments": [
            {
                "id": PAYMENT_ID,
                "value": total,
                "due_date": fecha
            }
        ]
    }

    return payload

