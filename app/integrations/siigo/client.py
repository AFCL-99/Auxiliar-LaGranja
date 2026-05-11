import httpx

from app.integrations.siigo.auth import get_token
from app.schemas.response import SiigoAPIError
import json


class SiigoClient:

    BASE_URL = "https://api.siigo.com/v1"

    async def request(
        self,
        method: str,
        endpoint: str,
        payload: dict | None = None,
        params: dict | None = None,
    ):

        token = await get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Partner-Id": "SiigoAPI",
        }

        url = f"{self.BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.request(
                method=method, url=url, headers=headers, json=payload, params=params
            )
        try:
            data = response.json()
            if response.status_code not in [200, 201]:
                raise SiigoAPIError(status_code=response.status_code, detail=data)

        except Exception:

            try:
                data = json.loads(response.text)

            except Exception:

                data = {"raw": response.text, "data": []}
        return {"status_code": response.status_code, "data": data}


siigo_client = SiigoClient()
