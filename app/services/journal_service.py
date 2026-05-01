import datetime

from app.services.flete_service import calcular_flete_factura

def construir_journal(factura_numero):
    data = calcular_flete_factura(factura_numero)

    items = []

    for d in data["detalle"]:
        items.append({
            "account": {"code": "1435010201", "movement": "Debit"},
            "customer": {
                "identification": data["proveedor"],
                "branch_office": 0
            },
            "product": {
                "id": d["id"],
                "code": d["code"],
                "name": d["name"],
                "quantity": 0
            },
            "description": d["name"],
            "value": d["valor"]
        })

    items.append({
        "account": {"code": "51355002", "movement": "Credit"},
        "customer": {
            "identification": data["proveedor"],
            "branch_office": 0
        },
        "description": "Servicio de transporte fletes",
        "value": data["totalFlete"]
    })

    return {
        "document": {"id": 40939},
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": items,
        "observations": f"FLETE FACTURA {factura_numero}"
    }