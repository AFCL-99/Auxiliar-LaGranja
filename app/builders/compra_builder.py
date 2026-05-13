from datetime import date
from typing import List

from app.core.constants import (
    COST_CENTER_ADMIN,
    DOCUMENT_COMPRA_ID,
    PAYMENT_CREDITO_ID,
    SIIGO_TAX_MAP,
)
from app.core.settings import PROVIDERS
from app.schemas.compra import FacturaCompra, Producto


def separar_factura_id(factura_id: str):
    prefijo, numero = factura_id.split("-")
    return prefijo, numero


def construir_payload_compra(factura: FacturaCompra):
    proveedor = factura.proveedor

    if proveedor not in PROVIDERS:
        raise Exception(f"Proveedor no soportado: {proveedor}")

    config_provider = PROVIDERS[proveedor]

    prefijo, numero = factura.separar_factura_id()

    items_siigo = mapear_items_siigo(factura.items, config_provider)
    fecha = date.today().strftime("%Y-%m-%d")
    total = 3560838.44

    payload = {
        "document": {"id": DOCUMENT_COMPRA_ID},
        "date": fecha,
        "cost_center": COST_CENTER_ADMIN,
        "supplier": config_provider["supplier"],
        "provider_invoice": {"prefix": prefijo, "number": numero},
        "discount_type": config_provider["discount"]["type"],
        "items": items_siigo,
        "payments": [
            {"id": PAYMENT_CREDITO_ID, "value": round(total, 2), "due_date": fecha}
        ],
    }
    return payload


def mapear_items_siigo(items: List[Producto], config):
    items_siigo = []

    warehouse = config["warehouse"]

    for item in items:

        impuestos = []

        iva = item.iva

        tax_id = SIIGO_TAX_MAP.get(int(iva))

        if tax_id:
            impuestos.append({"id": tax_id})
        retefuente = config.get("retefuente", {})

        if retefuente.get("enabled"):

            impuestos.append({"id": retefuente["tax_id"]})

        item_siigo = {
            "type": "Product",
            "code": str(item.codigo_Siigo),
            "quantity": item.cantidad,
            "price": item.valorUnitario,
            "warehouse": warehouse,
            "taxes": impuestos,
        }

        discount_config = config["discount"]

        if discount_config["type"] == "Percentage":

            item_siigo["discount"] = discount_config["value"]

        else:

            item_siigo["discount"] = item.descuento

        items_siigo.append(item_siigo)

    return items_siigo
