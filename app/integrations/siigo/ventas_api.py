from app.integrations.siigo.client import siigo_client


async def obtener_cotizacion(params):
    return await siigo_client.request(
        method="get", endpoint="/quotations", params=params
    )


async def obtener_facturas(created_start, created_end):
    results = []

    page = 1
    while True:
        params = {
            "created_start": created_start,
            "created_end": created_end,
            "page": page,
            "page_size": 50,
        }
        data = await siigo_client.request(
            method="GET", endpoint="/invoices", params=params
        )
        data = data.get("data", [])
        items = data.get("results", [])

        if not items:
            break

        results.extend(items)
        page += 1

    return results


async def obtener_vouchers(created_start, created_end):
    results = []

    page = 1

    while True:
        params = {
            "created_start": created_start,
            "created_end": created_end,
            "page": page,
            "page_size": 50,
        }
        data = await siigo_client.request(
            method="GET", endpoint="/vouchers", params=params
        )
        data = data.get("data", [])
        items = data.get("results", [])

        if not items:
            break

        results.extend(items)

        page += 1
    return results
