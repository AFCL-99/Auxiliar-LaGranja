from datetime import datetime, timedelta
import json

from app.integrations.siigo.compra_api import obtener_facturasCompra


async def buscar_factura_por_numero(numero: str):
    factura_buscada = str(numero).strip().upper()
    page = 1
    hoy = datetime.now()
    hace_dias = hoy - timedelta(days=60)

    created_start = hace_dias.strftime("%Y-%m-%d")
    created_end = hoy.strftime("%Y-%m-%d")

    while True:

        params = {
            "created_start": created_start,
            "created_end": created_end,
            "page": page,
            "page_size": 25,
        }

        data = await obtener_facturasCompra(params)
        resultados = data.get("data", [])

        if resultados:
            for f in resultados.get("results"):
                numero = str(f.get("number", "")).strip().upper()

                if numero == factura_buscada:
                    print(json.dumps(f, indent=4))
                    return f
