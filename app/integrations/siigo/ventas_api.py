from app.integrations.siigo.client import siigo_client


async def obtener_cotizacion(params):
    return await siigo_client.request(
        method="get", endpoint="/quotations", params=params
    )


async def crear_factura(param):

    pass
