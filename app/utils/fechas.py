from datetime import datetime, timedelta


def obtener_fecha_vencimiento(tipo):

    hoy = datetime.now()

    if tipo == "15":
        return (hoy + timedelta(days=15)).strftime("%Y-%m-%d")

    elif tipo == "fin_mes":
        siguiente_mes = hoy.replace(day=28) + timedelta(days=4)
        ultimo_dia = siguiente_mes - timedelta(days=siguiente_mes.day)

        return ultimo_dia.strftime("%Y-%m-%d")

    return hoy.strftime("%Y-%m-%d")
