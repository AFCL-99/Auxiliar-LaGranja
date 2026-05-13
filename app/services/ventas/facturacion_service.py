import json

from app.builders.venta_builder import construir_payload_venta


async def crear_facturaVenta_service(cotizacion: dict, vencimiento: str):
    payload = construir_payload_venta(cotizacion, vencimiento)
    print(json.dumps(payload, indent=4))
