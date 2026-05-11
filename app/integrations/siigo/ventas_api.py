from app.integrations.siigo.client import siigo_client


def buscar_cotizacion():
    pass


def crear_factura_desde_cotizacion():
    pass


async def buscar_ventas(params: dict):

    url = f"/invoices?created_start={fecha_inicio}&created_end={fecha_fin}&page={page}&page_size=100"
    return await siigo_client.request(method="GET", endpoint=url)
