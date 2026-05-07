from app.config.providers_config import PROVIDERS

def construir_payload(data):

    proveedor = data.get("proveedor")

    if proveedor not in PROVIDERS:
        raise Exception(f"Proveedor no soportado: {proveedor}")

    config = PROVIDERS[proveedor]

    return construir_generico(data, config)

RETEFUENTE_25 = 7321
DOCUMENT_ID = 14148
COST_CENTER = 367
PAYMENT_ID = 4390
BODEGA_PLANTAS_NEIVA = 73
BODEGA_PRINCIPAL = 69

TAX_MAP = {
    5: 7316,
    19: 7315
}
def separar_factura_id(factura_id):
    prefijo, numero = factura_id.split("-")
    return prefijo, numero

def construir_generico(data, config):

    factura_id = data["factura_id"]
    items = data["items"]
    fecha = data["fecha"]

    prefijo, numero = separar_factura_id(factura_id)

    items_siigo = mapear_items_siigo(
        items,
        config
    )

    total = calcular_total(
        items,
        config
    )

    payload = {

        "document": {
            "id": config["document_id"]
        },

        "date": fecha,

        "cost_center": config["cost_center"],

        "supplier": config["supplier"],

        "provider_invoice": {
            "prefix": prefijo,
            "number": numero
        },

        "discount_type": config["discount"]["type"],

        "items": items_siigo,

        "payments": [
            {
                "id": config["payment_id"],
                "value": total,
                "due_date": fecha
            }
        ]
    }

    return payload

def calcular_total(items, config):

    total = 0

    discount_config = config["discount"]

    for item in items:

        cantidad = item["cantidad"]
        precio = item["precio"]

        base = cantidad * precio

        # descuento
        if discount_config["type"] == "Percentage":

            descuento = (
                base * discount_config["value"] / 100
            )

        else:

            descuento = item.get("descuento", 0)

        base_final = base - descuento

        iva = (
            base_final *
            item.get("iva", 0) / 100
        )

        total += base_final + iva

    return round(total, 2)

def mapear_items_siigo(items, config):

    items_siigo = []

    warehouse = config["warehouse"]

    for item in items:

        impuestos = []

        # IVA
        iva = item.get("iva")

        tax_id = TAX_MAP.get(iva)

        if tax_id:
            impuestos.append({
                "id": tax_id
            })

        # RETEFUENTE
        retefuente = config.get("retefuente", {})

        if retefuente.get("enabled"):

            impuestos.append({
                "id": retefuente["tax_id"]
            })

        item_siigo = {
            "type": "Product",
            "code": str(item["codigo_siigo"]),
            "quantity": item["cantidad"],
            "price": item["precio"],
            "warehouse": warehouse,
            "taxes": impuestos
        }

        # descuento
        discount_config = config["discount"]

        if discount_config["type"] == "Percentage":

            item_siigo["discount"] = discount_config["value"]

        else:

            item_siigo["discount"] = item.get("descuento", 0)

        items_siigo.append(item_siigo)

    return items_siigo