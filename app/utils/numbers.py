from decimal import Decimal, ROUND_HALF_UP


def limpiar_numero(valor):
    valor = valor.replace("$", "").replace(",", "").strip()
    return float(valor) if valor else 0.0


def formatear_precio(valor):
    return float(Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def formatear_procentaje(valor):
    return f"{valor:.2%}"


def formatear_moneda(valor):
    return f"${valor:,.2f}"


def formatear_numero(valor):
    if not valor:
        return ""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
