# services/cierre/cierre_mapper.py

from app.repositories.clientes_repository import (
    obtener_nombre_cliente,
)
from app.schemas.cierre import FilaCierre


def mapear_facturas_cierre(
    facturas: list,
    df_clientes,
    cache_clientes: dict,
):

    filas = []

    for factura in facturas:

        nombre = factura.get("name", "")

        if not nombre.startswith("FV-03"):
            continue

        cliente_id = factura.get("customer", {}).get("identification", "")

        cliente = obtener_nombre_cliente(
            cliente_id,
            df_clientes,
            cache_clientes,
        )

        numero = nombre.replace("FV-03-", "")

        pagos = factura.get("payments", [])

        # SIN PAGOS
        if not pagos:

            filas.append(
                FilaCierre(
                    orden=int(numero),
                    fecha=factura.get("date", ""),
                    numero=numero,
                    cliente=cliente,
                    credito=factura.get("total", 0),
                )
            )

            continue

        # CON PAGOS
        for pago in pagos:

            metodo = (pago.get("name") or "").lower()

            valor = pago.get("value", 0)

            efectivo = 0
            credito = 0
            banco = 0
            metodo_mostrar = ""

            if "efectivo" in metodo:

                efectivo = valor

            elif "crédito" in metodo:

                credito = valor

            else:

                banco = valor
                metodo_mostrar = pago.get("name", "")

            filas.append(
                FilaCierre(
                    orden=int(numero),
                    fecha=factura.get("date", ""),
                    numero=numero,
                    cliente=cliente,
                    efectivo=efectivo,
                    credito=credito,
                    banco=banco,
                    metodo=metodo_mostrar,
                )
            )

    return filas


def mapear_vouchers_cierre(
    vouchers: list,
    df_clientes,
    cache_clientes: dict,
):

    from app.services.cierre.cierre_rules import (
        discriminar_pago_detailed,
        discriminar_pago_simple,
    )

    filas = []

    for voucher in vouchers:

        numero = f"RC-{voucher.get('number', '')}"

        cliente_id = voucher.get("customer", {}).get("identification", "")

        cliente = obtener_nombre_cliente(
            cliente_id,
            df_clientes,
            cache_clientes,
        )

        efectivo = 0
        banco = 0
        metodo = ""
        print(voucher)
        if voucher.get("type") == "Detailed":

            resultado = discriminar_pago_detailed(voucher)

        else:

            resultado = discriminar_pago_simple(voucher.get("payment", {}))

        efectivo = resultado["efectivo"]
        banco = resultado["banco"]
        metodo = resultado["metodo"]

        filas.append(
            FilaCierre(
                orden=999999,
                fecha=voucher.get("date", ""),
                numero=numero,
                cliente=cliente,
                cartera=efectivo,
                banco=banco,
                metodo=metodo,
            )
        )

    return filas
