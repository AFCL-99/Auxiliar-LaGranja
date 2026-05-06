from app.providers import contegral, italcol, alimentosPolar, gabrica, italcolDeOccidente
from app.services.siigo_api import obtener_factura, siigo_request

def detectar_y_procesar(texto):

    if "860,026,895-8" in texto:
        return italcol.procesar(texto)

    if "890901271-5" in texto:
        return contegral.procesar(texto)

    if "830.006.735-3" in texto:
        return alimentosPolar.procesar(texto)
    
    if "nit: 891304762-2" in texto:
        return italcolDeOccidente.procesar(texto)

    if "nit 800164767 - 6" in texto:
        return gabrica.procesar(texto)

    raise Exception("Proveedor no soportado")

def calcular_totales_factura(items):
    subtotal = 0
    total_iva = 0
    descuentoTotal = 0
    for item in items:
        cantidad = item["cantidad"]
        precio = item["precio"]
        descuento = item.get("descuento", 0)
        iva_porcentaje = item.get("iva", 0)

        descuento_unitario = descuento / cantidad if cantidad else 0

        # 🔹 precio final unitario
        precio_final = round(precio - descuento_unitario, 2)

        # 🔹 base línea
        base = round(precio_final * cantidad, 2)

        # 🔹 IVA
        iva = round(base * iva_porcentaje / 100, 2)

        subtotal += round(cantidad*precio,2)
        total_iva += iva
        descuentoTotal += descuento

    total = subtotal + total_iva - descuentoTotal

    return {
        "subtotal": round(subtotal, 2),
        "descuento": round(descuentoTotal,2),
        "iva": round(total_iva, 2),
        "total": round(total, 2)
    }

def limpiar_items_para_put(items, nueva_bodega):
    return [
        {
            "type": item["type"],
            "code": item["code"],
            "description": item["description"],
            "quantity": item["quantity"],
            "price": item["price"],
            "discount": item.get("discount", 0),
            "taxes": item.get("taxes", []),
            "warehouse": nueva_bodega
        }
        for item in items
    ]

def actualizar_bodega_factura(num_factura: int, nueva_bodega: int):

    original = obtener_factura(str(num_factura))
    endpoint = f"/purchases/{original.get("id")}"

    items_limpios = limpiar_items_para_put(original["items"], nueva_bodega)

    total_items = sum(
        item["quantity"] * item["price"]
        for item in items_limpios
    )
    total_final = round(total_items, 2)
    print(original)
    print("Total recalculado:", total_final)
    payload = {
        "document": {
            "id": int(original["document"]["id"])
        },
        "date": original["date"],
        "supplier": {
            "identification": original["supplier"]["identification"],
            "branch_office": original["supplier"]["branch_office"]
        },
        "provider_invoice": original.get("provider_invoice"),
        "cost_center": original.get("cost_center"),
        "supplier_by_item": False,
        "total": original.get("total"),
        "items": items_limpios,
        "payments": original.get("payments")
    }
    response = siigo_request(endpoint, method="put", payload=payload)

    return response