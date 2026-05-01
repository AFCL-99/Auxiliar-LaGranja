from app.services.auth_service import get_token
import requests
from datetime import datetime, timedelta
import re

def subir_factura_siigo(datos):
    
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Partner-Id": "SiigoAPI"
    }
    
    response = requests.post(
        "https://api.siigo.com/v1/purchases",
        json=datos,
        headers=headers
    )
    
    return response.json()


BASE_URL = "https://api.siigo.com/v1/purchases"
PARTNER_ID = "SiigoAPI"


def obtener_factura(numero_factura: str):

    factura_buscada = str(numero_factura).strip().upper()

    page_size = 25
    page = 1

    # 🔹 fechas
    hoy = datetime.now()
    hace_dias = hoy - timedelta(days=60)

    created_start = hace_dias.strftime("%Y-%m-%d")
    created_end = hoy.strftime("%Y-%m-%d")
    while True:

        token = get_token()

        params = {
            "created_start": created_start,
            "created_end": created_end,
            "page": page,
            "page_size": page_size
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Partner-Id": PARTNER_ID
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Error Siigo: {response.text}")

        data = response.json()

        resultados = data.get("results", [])

        if not resultados:
            break

        # 🔍 buscar factura
        for f in resultados:
            numero = str(f.get("number", "")).strip().upper()
            if numero == factura_buscada:
                return f

        page += 1


def actualizar_factura_siigo(id_factura, items_nuevos):

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Partner-Id": "SiigoAPI",
        "Content-Type": "application/json"
    }

    # 1️⃣ obtener factura original
    response = requests.get(BASE_URL + id_factura, headers=headers)
    original = response.json()

    total_calculado = 0
    # 3️⃣ actualizar payments
    pagos_actualizados = [
        {
            "id": p["id"],
            "value": total_calculado,
            "due_date": p["due_date"]
        }
        for p in original.get("payments", [])
    ]

    # 4️⃣ construir payload
    payload = {
        "document": {"id": original["document"]["id"]},
        "date": original["date"],
        "supplier": {
            "identification": original["supplier"]["identification"],
            "branch_office": original["supplier"]["branch_office"]
        },
        "provider_invoice": original.get("provider_invoice"),
        "cost_center": original.get("cost_center"),
        "supplier_by_item": False,
        "items": items_nuevos,
        "payments": pagos_actualizados
    }

    # 5️⃣ enviar
    put_response = requests.put(
        BASE_URL + id_factura,
        headers=headers,
        json=payload
    )

    data = put_response.json()

    # 🔥 6️⃣ manejar error de total
    if put_response.status_code == 400:
        total_siigo = extraer_total_desde_error(data)

        if total_siigo:
            payload["payments"][0]["value"] = total_siigo

            put_response = requests.put(
                BASE_URL + id_factura,
                headers=headers,
                json=payload
            )

            return put_response.json()

    return data


from datetime import datetime, timedelta


BASE_URL = "https://api.siigo.com/v1/purchases"

def obtener_factura_por_numero(numero_factura):

    factura_buscada = str(numero_factura).strip().upper()

    page_size = 25
    page = 1

    hoy = datetime.now()
    hace_dias = hoy - timedelta(days=60)

    created_start = hace_dias.strftime("%Y-%m-%d")
    created_end = hoy.strftime("%Y-%m-%d")

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Partner-Id": "SiigoAPI"
    }

    while True:

        params = {
            "created_start": created_start,
            "created_end": created_end,
            "page": page,
            "page_size": page_size
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Error Siigo: {response.text}")

        data = response.json()
        resultados = data.get("results", [])

        if not resultados:
            break

        for f in resultados:
            numero = str(f.get("number", "")).strip().upper()

            if numero == factura_buscada:
                return f  # 🔥 devuelves TODO (mejor que solo id)

        # 🔴 importante: cortar correctamente
        if not data.get("pagination") or page >= data["pagination"]["total_pages"]:
            break

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