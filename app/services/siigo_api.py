import json
from app.config.recibo_pago_config import FLETES_SIIGO
from app.services.auth_service import get_token
import requests
from datetime import datetime, timedelta
import re

from app.utils.htmlToPdf import generar_pdf

BASE_URL = "https://api.siigo.com/v1"

def siigo_request(endpoint, method="get", payload=None, params=None):

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Partner-Id": "SiigoAPI"
    }

    url = BASE_URL + endpoint
    method = method.lower()

    print(f"{method.upper()} -> {url}")

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=payload,
        params=params
    )

    try:
        data = response.json()
    except Exception:
        data = {
            "raw": response.text
        }

    if isinstance(data, dict):
        data["status"] = response.status_code

    if response.status_code not in [200, 201]:
        print("ERROR SIIGO:", data)
        return data

    return data

def subir_factura_siigo(datos):
    response = siigo_request(
        endpoint="/purchases",
        method="post",
        payload=datos
    )
    return response

def obtener_factura(numero_factura: str):
    print("Obteniendo factura: " + numero_factura)

    factura_buscada = str(numero_factura).strip().upper()

    page_size = 25
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
            "page_size": page_size
        }

        data = siigo_request(
            endpoint="/purchases",
            method="get",
            params=params
        )

        resultados = data.get("results", [])

        if not resultados:
            break

        for f in resultados:
            numero = str(f.get("number", "")).strip().upper()

            if numero == factura_buscada:
                print("FACTURA ENCONTRADA")
                return f

        page += 1

    raise Exception("Factura no encontrada")


def extraer_total_desde_error(response_json):
    print("extrayendo total del error")
    try:
        error = response_json["errors"][0]
        mensaje = error["message"]

        match = re.search(r"is ([\d\.]+)", mensaje)

        if match:
            return float(match.group(1))

    except Exception:
        pass

    return None

def crear_factura_desde_cotizacion(numero, fecha_vencimiento):

    cot = buscar_cotizacion(numero)

    items_factura = [
        {
            "code": i["code"],
            "description": i["description"],
            "quantity": i["quantity"],
            "price": i["price"],
            "discount": i.get("discount", 0),
            "warehouse": 69,
            "taxes": i.get("taxes"),
            "taxpayer": i.get("taxpayer")
        }
        for i in cot["items"]
    ]

    payload = {
        "document": {"id": 28047},
        "date": datetime.now().strftime("%Y-%m-%d"),

        "customer": {
            "identification": cot["customer"]["identification"],
            "branch_office": cot["customer"].get("branch_office", 0)
        },

        "seller": cot.get("seller"),

        "payments": [
            {
                "id": 4385,
                "value": cot["total"],
                "due_date": fecha_vencimiento
            }
        ],

        "items": items_factura
    }
    print(json.dumps(payload, indent=4))
    
    resp = siigo_request("/invoices", "post", payload)

    if resp.get("Errors"):
        raise Exception(resp["Errors"])

    return resp


def buscar_cotizacion(numero):

    consecutivo = f"C-2-{numero}"

    resp = siigo_request(
        "/quotations",
        "get",
        params={"name": consecutivo}
    )

    if not resp.get("results"):
        raise Exception("Cotización no encontrada")

    return resp["results"][0]

    
def crear_flete_pago(nombre, valor, fecha, recibo, banco):

    tercero = FLETES_SIIGO[nombre]

    payload = {

        "document": {
            "id": 14147
        },

        "date": fecha.strftime("%Y-%m-%d"),

        "type": "AdvancePayment",

        "supplier": {
            "identification": tercero["identification"],
            "branch_office": 0
        },

        "observations": f"CONSIGNACION {banco} RCBO {recibo}",

        "payment": {
            "id": 4389,
            "value": valor
        }
    }
    response = subir_pago_flete(payload)
    return generar_pdf(tercero,response)

def subir_pago_flete(datos):
    response = siigo_request(
        endpoint="/payment-receipts",
        method="post",
        payload=datos
    )
    print(response.get("number"))
    return response

def subir_pago_flete_prueba(datos):
    return {
            "id": "e1c8432a-8a2d-4b62-905c-0a878a569fab",
            "document": {
                "id": 14147
            },
            "number": 7682,
            "name": "RP-1-7682",
            "date": "2026-05-07",
            "type": "AdvancePayment",
            "supplier": {
                "id": "7305afc6-9ca5-4747-b3c7-a956077d32b3",
                "identification": "30509423",
                "branch_office": 0
            },
            "observations": "CONSIGNACION davivienda RCBO 445152",
            "payment": {
                "id": 4389,
                "value": 2127600.0
            },
            "metadata": {
                "created": "2026-05-07T10:58:22"
            },
            "status": 201
        }