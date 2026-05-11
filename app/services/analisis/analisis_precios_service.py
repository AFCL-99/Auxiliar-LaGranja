from app.services.analisis.historico_service import obtener_precio_historico


def analizar_factura(factura: dict):

    productos = factura.get("items", [])
    comprobante_actual = f"{factura.get('prefix','')}{factura.get('number','')}"
    salida = []

    for p in productos:
        precio_actual = p.get("price", 0)

        if precio_actual == 0:
            continue

        codigo = str(p.get("code")).strip()
        descripcion = p.get("description", "")

        historico = obtener_precio_historico(codigo, comprobante_actual)

        precio_anterior = historico.get("precio", 0)

        diferencia = precio_actual - precio_anterior

        porcentaje = diferencia / precio_anterior if precio_anterior > 0 else 0

        # 🔥 estados
        if not precio_anterior:
            estado = "✚"

        elif precio_actual > precio_anterior:
            estado = "▲"

        elif precio_actual < precio_anterior:
            estado = "▼"

        else:
            estado = "▬"

        salida.append(
            {
                "codigo": codigo,
                "descripcion": descripcion,
                "precio_anterior": precio_anterior,
                "precio_actual": precio_actual,
                "diferencia": diferencia,
                "porcentaje": porcentaje,
                "estado": estado,
                "fecha": historico.get("fecha"),
                "comprobante": historico.get("factura"),
            }
        )

    return {"items": salida}
