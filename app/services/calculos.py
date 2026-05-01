def calcular_totales(items):
    subtotal = 0
    total_iva = 0
    descuentoTotal = 0
    for item in items:
        cantidad = item["cantidad"]
        precio = item["precio"]
        descuento = item.get("descuento", 0)
        iva_porcentaje = item.get("iva", 0)

        # 🔹 descuento por unidad
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