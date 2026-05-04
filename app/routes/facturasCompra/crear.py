from fastapi import Form, APIRouter, UploadFile
from app.utils.temp_store import temp_data
from app.services.siigo_api import extraer_total_desde_error, subir_factura_siigo
from app.services.siigo_builder import construir_payload
import re

router = APIRouter(prefix="/compra", tags=["compra"])
@router.post("/crear")
def confirmar(id_proceso: str = Form(...)):
    
    data = temp_data.get(id_proceso)

    if not data:
        return {"error": "Proceso no encontrado"}
    
    for item in data["items"]:
        if not item.get("codigo_siigo"):
            raise Exception(f"Producto sin código Siigo: {item}")

    payload = construir_payload(data)
    response = subir_factura_siigo(payload)
    data = response

    print(response)
    if response.get("status") in [200, 201]:
        return data

    if data.get("errors"):
        code = data["errors"][0].get("code")

        if code == "invalid_total_payments":

            total_correcto = extraer_total_desde_error(data)

            if total_correcto:
                print("🔁 Reintentando con total:", total_correcto)

                # 🔥 actualizar payment
                payload["payments"][0]["value"] = total_correcto

                # 🔁 reenviar
                response = subir_factura_siigo(payload)
                return response

    del temp_data[id_proceso]
    return data

