import requests, datetime
from app.services.auth_service import get_token

def calcular_flete_factura(numero_factura):
    return "pendiente"

def existe_flete(factura_numero):
    print("existe flete?: "+factura_numero)
    today = datetime.datetime.now() 
    start = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    page = 1
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Partner-Id": "SiigoAPI"
    }
    while True:

        url = f"https://api.siigo.com/v1/journals?created_start={start}&created_end={end}&page={page}&page_size=50"
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data.get("results"):
            break

        for j in data["results"]:
            obs = str(j.get("observations", ""))
            if f"FLETE FACTURA {factura_numero}" in obs:
                return True

        page += 1

    return False

def obtener_fletes_existentes():
    print("obtener fletes existentes")
    resultados = []
    token = get_token()
    today = datetime.datetime.now()
    start = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    page = 1    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Partner-Id": "SiigoAPI"
    }
    while True:
        url = f"https://api.siigo.com/v1/journals?created_start={start}&created_end={end}&page={page}&page_size=50"
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data.get("results"):
            break

        for j in data["results"]:

            obs = j.get("observations", "")
            if "FLETE FACTURA" in obs:
                resultados.append({
                    "fecha": j.get("date"),
                    "observacion": obs,
                    "id": j.get("name")
                })

        page += 1

    return resultados