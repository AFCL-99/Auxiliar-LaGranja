from app.integrations.siigo.client import siigo_client


async def obtener_planilla_siigo(params):
    return await siigo_client.request(
        method="get", endpoint="/accounts-payable", params=params
    )
