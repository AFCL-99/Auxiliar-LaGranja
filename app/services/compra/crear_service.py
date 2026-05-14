from app.builders.compra_builder import construir_payload_compra
from app.integrations.siigo.compra_api import subir_factura_compra
from app.repositories.preview_repository import get_preview
from app.services.compra.response_handler import manejar_respuesta_siigo


async def crear_factura_service(process_id):

    factura = get_preview(process_id)
    if not factura:
        raise Exception("Preview no encontrada")

    payload = construir_payload_compra(factura)
    response = await subir_factura_compra(payload)
    manejo = manejar_respuesta_siigo(response)
    if manejo.get("mensaje") == "SIIGO rechazó la factura por diferencia en el total.":
        payload["payments"][0]["value"] = manejo.get("valor")

    response = await subir_factura_compra(payload)
    return manejar_respuesta_siigo(response)
