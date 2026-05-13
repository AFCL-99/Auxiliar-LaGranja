from app.integrations.siigo.ventas_api import obtener_cotizacion


async def buscar_cotizacion_por_numero(numero: str) -> dict:
    nombreCotizacion = f"c-2-{numero}"

    return await obtener_cotizacion(params={"name": nombreCotizacion})
