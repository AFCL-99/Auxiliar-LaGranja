from app.integrations.siigo.client import siigo_client


async def subir_factura_compra(payload):
    return await siigo_client.request(
        method="POST", endpoint="/purchases", payload=payload
    )


async def obtener_facturasCompra(params):
    return await siigo_client.request(
        method="get", endpoint="/purchases", params=params
    )
