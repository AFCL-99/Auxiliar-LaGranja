import json
import re


def manejar_respuesta_siigo(response):
    print(json.dumps(response, indent=4))
    if response["status_code"] in [200, 201]:

        return {
            "ok": True,
            "mensaje": "Factura creada correctamente",
            "siigo": response["data"],
        }

    error = obtener_primer_error(response)

    if error and es_codigo_inactivo(error):

        codigo = extraer_codigo_inactivo(error)

        return {
            "ok": False,
            "mensaje": f"El código {codigo} está inactivo",
            "detalle": error,
        }
    if error and es_total_pago_incorrecto(error):
        valor = extraer_total_siigo(error)

        return {
            "ok": False,
            "mensaje": "SIIGO rechazó la factura por diferencia en el total.",
            "valor": valor,
            "detalle": error,
        }
    return {
        "ok": False,
        "mensaje": "SIIGO rechazó la factura",
        "detalle": response["data"],
    }


def obtener_primer_error(response):

    errores = response["data"].get("errors", [])

    if not errores:
        return None

    return errores[0]


def es_codigo_inactivo(error):

    return error.get("code") == "parameter_inactive"


def es_total_pago_incorrecto(error):
    return error.get("code") == "invalid_total_payments"


def extraer_codigo_inactivo(error):

    mensaje = error.get("message", "")

    match = re.search(r"(\d+)", mensaje)

    if match:
        return match.group(1)

    return None


def extraer_total_siigo(error):
    mensaje = error.get("message", "")
    match = re.search(
        r"total purchase calculated is\s+([\d.]+)", mensaje, re.IGNORECASE
    )

    if not match:
        return None
    return round(float(match.group(1)), 2)
