import json
from colorama import Fore, Style, init
init(autoreset=True)
import requests
from app.services.leerExcel import cargar_clientes, mapear_clientes
BASE_URL = "https://api.siigo.com/v1"

def obtener_cierre(token, fecha):

    headers = {
        "Authorization": f"Bearer {token}",
        "Partner-Id": "GoogleSheetsIntegration"
    }

    fecha_inicio = f"{fecha}T00:00:00"
    fecha_fin = f"{fecha}T23:59:59"
    df_clientes = cargar_clientes("app/data/Clientes.xlsx")
    rows = []
    rc_rows = []
    cache_clientes = {}

    def obtener_nombre_cliente(identificacion):
        return mapear_clientes(identificacion,df_clientes,cache_clientes)

    # =============================
    # 1️⃣ FACTURAS (FV-03)
    # =============================
    page = 1

    while True:
        url = f"{BASE_URL}/invoices?created_start={fecha_inicio}&created_end={fecha_fin}&page={page}&page_size=100"

        data = requests.get(url, headers=headers).json()

        if not data.get("results"):
            break

        for f in data["results"]:

            if not f.get("name", "").startswith("FV-03"):
                continue

            if f.get("date") != fecha:
                continue

            if not f.get("payments"):
                continue

            numero = int(f["name"].replace("FV-03-", ""))
            cliente = obtener_nombre_cliente(f["customer"]["identification"])

            for pago in f["payments"]:

                metodo = (pago.get("name") or "").lower()
                valor = pago.get("value", 0)
                valor = formatear_numero(valor)
                efectivo = crédito = banco = ""
                metodoMostrar = pago.get("name", "")
                if "efectivo" in metodo:
                    efectivo = valor
                    metodoMostrar = ""
                elif "crédito" in metodo:
                    crédito = valor
                    metodoMostrar = ""
                else:
                    banco = valor

                rows.append({
                    "orden": numero,
                    "data": [
                        f["date"],
                        "",
                        cliente,
                        f["name"].replace("FV-03-", ""),
                        "",
                        efectivo,
                        crédito,
                        banco,
                        metodoMostrar
                    ]
                })

        page += 1

    rows.sort(key=lambda x: x["orden"])
    rows_final = [r["data"] for r in rows]

    # =============================
    # 2️⃣ VOUCHERS (RC)
    # =============================

    page = 1

    while True:
        url = f"{BASE_URL}/vouchers?created_start={fecha_inicio}&created_end={fecha_fin}&page={page}&page_size=100"

        data = requests.get(url, headers=headers).json()

        if not data.get("results"):
            break

        for v in data["results"]:

            if v.get("date") != fecha:
                continue

            numero = f"RC-{v.get('number', '')}"
            cliente_id = v.get("customer", {}).get("identification", "")
            cliente = obtener_nombre_cliente(cliente_id)

            total_credito = total_efectivo = total_bancos = total_ajustes = 0
            valor = 0
            metodo = ""

            if v.get("type") == "Detailed":
                resultado = discriminar_pagos(v)

                total_credito = resultado["facturas_pagadas"]
                total_efectivo = resultado["pagado_efectivo"]
                total_bancos = resultado["pagado_bancos"]
                total_ajustes = resultado["ajustes"]

                valor = total_efectivo + total_bancos

            else:
                payment = v.get("payment", {})
                valor = payment.get("value", 0)
                metodo = (payment.get("name") or "").lower()

                total_credito = sum(i.get("value", 0) for i in v.get("items", []))

                total_efectivo = 0
                total_bancos = 0

                if "efectivo" in metodo:
                    total_efectivo = valor
                else:
                    total_bancos = valor

            # =============================
            # FORMATEOS
            # =============================
            print(Fore.CYAN + f"RC: {numero}")
            print(Fore.YELLOW + f"Cliente: {cliente}")

            print(Fore.GREEN + f"Efectivo: {total_efectivo}")
            print(Fore.BLUE + f"Banco: {total_bancos}")
            print(Fore.MAGENTA + f"Cartera: {total_credito}")
            print(Fore.RED + f"Ajustes: {total_ajustes}")

            print(Style.DIM + "-"*40)
            valor_fmt = formatear_numero(valor)
            efectivo_fmt = formatear_numero(total_efectivo)
            banco_fmt = formatear_numero(total_bancos)
            cartera_fmt = formatear_numero(total_credito)

            observacion = (v.get("observations") or "").lower()
            es_detailed = v.get("type") == "Detailed"

            es_efectivo = False
            es_banco = False

            if es_detailed:
                if "efectivo" in observacion:
                    es_efectivo = True
                elif "bancolombia" in observacion or "davivienda" in observacion:
                    es_banco = True
                    if "davivienda" in observacion:
                        metodo = "DAVIVIENDA"
                    if "bancolombia" in observacion:
                        metodo = "BANCOLOMBIA"
            else:
                metodo_lower = metodo.lower()
                es_efectivo = "efectivo" in metodo_lower
                es_banco = not es_efectivo

            tiene_factura = any(i.get("due") for i in v.get("items", []))

            efectivo = cartera = banco = ""

                # 🔥 REGLA BASE: usar datos contables, no texto
            efectivo = ""  # ❌ nunca se usa en tu modelo
            cartera = ""
            banco = ""

            if es_detailed:

                # 💥 MIXTO
                if total_efectivo > 0 and total_bancos > 0:
                    cartera = efectivo_fmt   # 👈 SOLO el efectivo va a cartera
                    banco = banco_fmt

                    if "bancolombia" in observacion:
                        metodo = "BANCOLOMBIA"
                    elif "davivienda" in observacion:
                        metodo = "DAVIVIENDA"

                # 💵 SOLO EFECTIVO
                elif total_efectivo > 0:
                    cartera = efectivo_fmt   # 👈 TODO va a cartera
                    metodo = ""

                # 🏦 SOLO BANCO
                elif total_bancos > 0:
                    banco = banco_fmt

                    if "bancolombia" in observacion:
                        metodo = "BANCOLOMBIA"
                    elif "davivienda" in observacion:
                        metodo = "DAVIVIENDA"
                        

            else:
              
                if v.get("payment"):
                    metodo_lower = metodo.lower()
                    print(metodo_lower)
                    if "efectivo" in metodo_lower:
                        cartera = valor_fmt   # 👈 efectivo siempre a cartera
                        metodo = ""
                    else:
                        banco = valor_fmt

                        if "bancolombia" in metodo_lower:
                            metodo = "BANCOLOMBIA"
                        elif "davivienda" or "datafono" in metodo_lower:
                            metodo = "DAVIVIENDA"
                        elif "caja plantas" in metodo_lower:
                            metodo = "CAJA PLANTA"
            if total_efectivo > 0:
                cartera = efectivo_fmt
            rc_rows.append([
                v.get("date"),
                numero,
                cliente,
                "",
                cartera,
                efectivo,
                "",
                banco,
                metodo
            ])

        page += 1

    # =============================
    # 3️⃣ SEPARADOR + COMBINAR
    # =============================

    rows_final.append([
        fecha,
        "",
        "",
        "RM-1-",
        "",
        "",
        "",
        "",
        ""
    ])

    rows_final.extend(rc_rows)

    return rows_final


def formatear_numero(valor):
    if not valor:
        return ""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def discriminar_pagos(v):
    items = v.get("items", [])

    total_credito = 0
    total_efectivo = 0
    total_bancos = 0
    total_ajustes = 0

    for i in items:
        valor = i.get("value", 0)
        cuenta = i.get("account", {}).get("code", "")
        movimiento = i.get("account", {}).get("movement", "")

        if movimiento == "Credit":
            total_credito += valor

        elif movimiento == "Debit":
            if cuenta.startswith("1105"):
                total_efectivo += valor
            elif cuenta.startswith("1110"):
                total_bancos += valor
            else:
                total_ajustes += valor

    # 🔥 SI NO HAY DEBITOS → inferir desde observación
    if total_efectivo == 0 and total_bancos == 0 and total_credito > 0:

        obs = (v.get("observations") or "").lower()

        if "banco" in obs or "bancolombia" in obs or "davivienda" in obs:
            total_bancos = total_credito - total_ajustes
        else:
            total_efectivo = total_credito - total_ajustes

    return {
        "facturas_pagadas": total_credito,
        "pagado_efectivo": total_efectivo,
        "pagado_bancos": total_bancos,
        "total_pagado": total_efectivo + total_bancos,
        "ajustes": total_ajustes
    }