import json
from app.services.auth_service import get_token
import requests
from datetime import datetime, timedelta
import re

BASE_URL = "https://api.siigo.com/v1"

def siigo_request(endpoint, method="get", payload=None, params=None):

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Partner-Id": "SiigoAPI"
    }

    url = BASE_URL + endpoint
    print("URL:", url)

    if method.lower() == "get":
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        print("ERROR SIIGO:", response.text)
        raise Exception(f"Error Siigo {response.status_code}")

    return response.json()

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


def obtener_fecha_vencimiento(tipo):

    hoy = datetime.now()

    if tipo == "hoy":
        return hoy.strftime("%Y-%m-%d")

    elif tipo == "15":
        return (hoy + timedelta(days=15)).strftime("%Y-%m-%d")

    elif tipo == "fin_mes":
        siguiente_mes = hoy.replace(day=28) + timedelta(days=4)
        ultimo_dia = siguiente_mes - timedelta(days=siguiente_mes.day)

        return ultimo_dia.strftime("%Y-%m-%d")