import re
from fastapi import Form, APIRouter
from app.utils.temp_store import temp_data
from app.services.siigo_api import subir_factura_siigo
from app.services.siigo_builder import construir_payload
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/compra", tags=["compra"])


@router.post("/crear")
def confirmar(id_proceso: str = Form(...)):

    data = temp_data.get(id_proceso)

    if not data:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    try:
        validar_items_siigo(data.get("items", []))

        payload = construir_payload(data)

        response = subir_factura_siigo(payload)

        resultado = manejar_respuesta_siigo(
            response=response,
            payload=payload
        )

        if resultado.get("ok"):
            temp_data.pop(id_proceso, None)

        return resultado

    except Exception as e:
        return error_response(
            mensaje="Error interno al crear la factura.",
            detalle=str(e)
        )


def validar_items_siigo(items):
    for item in items:
        if not item.get("codigo_siigo"):
            raise Exception(f"Producto sin código SIIGO: {item}")


def manejar_respuesta_siigo(response, payload):

    if es_respuesta_exitosa_siigo(response):
        return success_response(
            response,
            "Factura creada correctamente en SIIGO."
        )

    error = obtener_primer_error(response)

    if not error:
        return error_response(
            mensaje="SIIGO rechazó la factura.",
            detalle=response
        )

    code = error.get("code")

    if code == "invalid_total_payments":
        return manejar_error_total_incorrecto(
            response=response,
            payload=payload
        )

    if es_error_producto(code):
        return manejar_error_producto(error)

    return error_response(
        mensaje=error.get("message", "SIIGO rechazó la factura."),
        detalle=code
    )


def manejar_error_total_incorrecto(response, payload):

    total_correcto = extraer_total_desde_error(response)

    if not total_correcto:
        return error_response(
            mensaje="SIIGO rechazó la factura por diferencia en el total.",
            detalle="invalid_total_payments"
        )

    payload["payments"][0]["value"] = total_correcto

    response_retry = subir_factura_siigo(payload)

    if es_respuesta_exitosa_siigo(response_retry):
        return success_response(
            response_retry,
            "Factura creada correctamente después de ajustar el total automáticamente."
        )

    error_retry = obtener_primer_error(response_retry)

    return error_response(
        mensaje="SIIGO rechazó la factura incluso después de ajustar el total.",
        detalle=error_retry.get("code") if error_retry else response_retry
    )


def manejar_error_producto(error):

    codigo_producto = extraer_codigo_producto_error(error)

    if codigo_producto:
        return error_response(
            mensaje=f"Producto inactivo o inválido en SIIGO: {codigo_producto}",
            detalle=codigo_producto
        )

    return error_response(
        mensaje="Hay un producto inactivo o inválido en SIIGO.",
        detalle=error.get("code")
    )


def es_respuesta_exitosa_siigo(response):
    return (
        isinstance(response, dict)
        and response.get("id")
        and response.get("number")
        and not response.get("errors")
    )


def obtener_primer_error(response):
    if not isinstance(response, dict):
        return None

    errores = response.get("errors", [])

    if not errores:
        return None

    return errores[0]


def extraer_total_desde_error(response):

    error = obtener_primer_error(response)

    if not error:
        return None

    mensaje = error.get("message", "")

    match = re.search(
        r"total purchase calculated is\s+([\d.]+)",
        mensaje,
        re.IGNORECASE
    )

    if not match:
        return None

    return round(float(match.group(1)), 2)


def es_error_producto(code):
    return code in [
        "invalid_product",
        "inactive_product",
        "product_inactive",
        "invalid_item"
    ]


def extraer_codigo_producto_error(error):

    texto = " ".join([
        str(error.get("message", "")),
        str(error.get("detail", "")),
        str(error.get("params", ""))
    ])

    match = re.search(
        r"\b[A-Z]{2,5}\d{2,6}\b",
        texto.upper()
    )

    if match:
        return match.group(0)

    return None


def success_response(response, mensaje):

    return {
        "ok": True,
        "mensaje": mensaje,
        "siigo": {
            "id": response.get("id"),
            "number": response.get("number"),
            "name": response.get("name"),
            "date": response.get("date"),
            "total": response.get("total")
        }
    }


def error_response(mensaje, detalle=None):

    return {
        "ok": False,
        "mensaje": mensaje,
        "detalle": detalle
    }



def subir_factura_siigo_caso_correcto(datos):

    return {
        "id": "950a8516-7644-4081-b9fe-818a15151641",
        "document": {
            "id": 14148
        },
        "number": 7330,
        "name": "FC-1-7330",
        "date": "2026-05-08",
        "cost_center": 367,
        "supplier": {
            "id": "abe408cf-0b6a-4048-8d4e-1d6053b34fea",
            "identification": "890901271",
            "branch_office": 0
        },
        "total": 49593576.81
    }