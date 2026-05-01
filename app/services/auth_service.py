import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# 🔹 cache en memoria
_token_cache = {
    "access_token": None,
    "expires_at": 0
}

# 🔹 credenciales (luego las pasamos a .env)
USERNAME = os.getenv("SIIGO_USERNAME")
ACCESS_KEY = os.getenv("SIIGO_ACCESS_KEY")
PARTNER_ID = os.getenv("SIIGO_PARTNER_ID") 

def get_token():
    global _token_cache

    # 🔥 si el token aún es válido, usarlo
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    # 🔄 pedir nuevo token
    response = requests.post(
        "https://api.siigo.com/auth",
        json={
            "username": USERNAME,
            "access_key": ACCESS_KEY
        },
        headers={
            "Partner-Id": PARTNER_ID,
            "Content-Type": "application/json"
        }
    )

    data = response.json()

    if "access_token" not in data:
        raise Exception(f"Error obteniendo token: {data}")

    # ⏱ guardar en cache (ej: 50 min)
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + (60 * 50)

    return _token_cache["access_token"]