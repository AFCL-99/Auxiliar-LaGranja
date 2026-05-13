from datetime import datetime
import json


def construir_payload_venta(cotizacion: dict, fechaVencimiento: str) -> dict:
    print(json.dumps(cotizacion, indent=4))
    items_factura = [
        {
            "code": i["code"],
            "description": i["description"],
            "quantity": i["quantity"],
            "price": i["price"],
            "discount": i.get("discount", 0),
            "warehouse": 69,
            "taxes": i.get("taxes"),
            "taxpayer": i.get("taxpayer"),
        }
        for i in cotizacion["items"]
    ]

    payload = {
        "document": {"id": 28047},
        "date": datetime.now().strftime("%Y-%m-%d"),
        "customer": {
            "identification": cotizacion["customer"]["identification"],
            "branch_office": cotizacion["customer"].get("branch_office", 0),
        },
        "seller": cotizacion.get("seller"),
        "payments": [
            {"id": 4385, "value": cotizacion["total"], "due_date": fechaVencimiento}
        ],
        "items": items_factura,
    }
    return payload
