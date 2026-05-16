from datetime import datetime

from app.integrations.siigo.ventas_api import (
    obtener_facturas,
    obtener_vouchers,
)
from app.repositories.clientes_repository import (
    cargar_clientes,
)
from app.services.cierre.cierre_mapper import (
    mapear_facturas_cierre,
    mapear_vouchers_cierre,
)


async def obtener_cierre_diario():
    fecha = str(datetime.now().date())

    created_start = f"{fecha}T00:00:00"

    created_end = f"{fecha}T23:59:59"

    df_clientes = cargar_clientes()

    cache_clientes = {}

    facturas = await obtener_facturas(created_start, created_end)
    vouchers = await obtener_vouchers(created_start, created_end)
    filas_facturas = mapear_facturas_cierre(
        facturas,
        df_clientes,
        cache_clientes,
    )

    filas_vouchers = mapear_vouchers_cierre(
        vouchers,
        df_clientes,
        cache_clientes,
    )
    filas_facturas.sort(key=lambda x: x.orden)

    filas_finales = []

    for fila in filas_facturas:
        filas_finales.append(fila)

    filas_finales.append({"separador": True})

    for fila in filas_vouchers:
        filas_finales.append(fila)

    return filas_finales
