# services/cierre/cierre_rules.py


def detectar_metodo_banco(texto: str) -> str:

    texto = (texto or "").lower()

    if "bancolombia" in texto:
        return "BANCOLOMBIA"

    if "davivienda" in texto:
        return "DAVIVIENDA"

    if "datafono" in texto:
        return "DAVIVIENDA"

    if "caja plantas" in texto:
        return "CAJA PLANTA"

    return ""


def discriminar_pago_simple(payment: dict):

    metodo = (payment.get("name") or "").lower()

    valor = payment.get("value", 0)

    efectivo = 0
    banco = 0
    metodo_mostrar = ""

    if "efectivo" in metodo:

        efectivo = valor

    else:

        banco = valor
        metodo_mostrar = detectar_metodo_banco(metodo)

    return {
        "efectivo": efectivo,
        "banco": banco,
        "metodo": metodo_mostrar,
    }


def discriminar_pago_detailed(voucher: dict):

    observacion = (voucher.get("observations") or "").lower()

    pagos = voucher.get("payments", [])

    total_efectivo = 0
    total_bancos = 0

    for pago in pagos:
        print(pago)
        metodo = (pago.get("name") or "").lower()

        valor = pago.get("value", 0)

        if "efectivo" in metodo:

            total_efectivo += valor

        else:

            total_bancos += valor

    metodo = detectar_metodo_banco(observacion)

    return {
        "efectivo": total_efectivo,
        "banco": total_bancos,
        "metodo": metodo,
    }
