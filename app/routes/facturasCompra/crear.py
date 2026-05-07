import json

from fastapi import Form, APIRouter, UploadFile
from app.utils.temp_store import temp_data
from app.services.siigo_api import extraer_total_desde_error, subir_factura_siigo
from app.services.siigo_builder import construir_payload
from app.pruebas import response_ok
import re

router = APIRouter(prefix="/compra", tags=["compra"])

@router.post("/crear")
def confirmar(id_proceso: str = Form(...)):
    data = temp_data.get(id_proceso)

    if not data:
        return {
            "ok": False,
            "mensaje": "Proceso no encontrado o expirado.",
            "detalle": None
        }

    try:
        validar_items_siigo(data["items"])

        payload = construir_payload(data)

        print("PAYLOAD SIIGO:")
        print(json.dumps(payload, indent=4))

        #response = subir_factura_siigo(payload)
        response = response_ok
        resultado = manejar_respuesta_siigo(
            response=response,
            payload=payload
        )

        if resultado["ok"]:
            temp_data.pop(id_proceso, None)

        return resultado

    except Exception as e:
        return {
            "ok": False,
            "mensaje": "Error interno al crear la factura.",
            "detalle": str(e)
        }
def validar_items_siigo(items):
    for item in items:
        if not item.get("codigo_siigo"):
            raise Exception(f"Producto sin código Siigo: {item}")
        

def respuesta_exitosa(response, mensaje_extra=None):

    data = response.get("data", response)

    return {
        "ok": True,
        "mensaje": mensaje_extra or "Factura creada correctamente en SIIGO.",
        "siigo": data
    }

def respuesta_error(response):

    errores = response.get("errors", [])

    if errores:
        mensaje = errores[0].get("message") or errores[0].get("Message")
        detalle = errores[0]
    else:
        mensaje = "SIIGO rechazó la factura."
        detalle = response

    return {
        "ok": False,
        "mensaje": mensaje,
        "detalle": detalle
    }
def manejar_respuesta_siigo(response, payload):

    if response.get("status") in [200, 201]:
        return respuesta_exitosa(response)

    errores = response.get("errors", [])

    if errores:
        code = errores[0].get("code")

        if code == "invalid_total_payments":
            total_correcto = extraer_total_desde_error(response)

            if total_correcto:
                print("🔁 Reintentando con total:", total_correcto)

                payload["payments"][0]["value"] = total_correcto

                response_retry = subir_factura_siigo(payload)

                if response_retry.get("status") in [200, 201]:
                    return respuesta_exitosa(
                        response_retry,
                        mensaje_extra="Factura creada después de corregir el total automáticamente."
                    )

                return respuesta_error(response_retry)

    return respuesta_error(response)
