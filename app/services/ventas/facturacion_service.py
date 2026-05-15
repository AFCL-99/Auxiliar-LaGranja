import json

from app.builders.venta_builder import construir_payload_venta
from app.utils.fechas import obtener_fecha_vencimiento


async def crear_facturaVenta_service(cotizacion, vencimiento: str):
    fecha_vencimiento = obtener_fecha_vencimiento(vencimiento)
    data = cotizacion.get("results")
    payload = construir_payload_venta(data[0], fecha_vencimiento)
    print(json.dumps(payload, indent=4))
