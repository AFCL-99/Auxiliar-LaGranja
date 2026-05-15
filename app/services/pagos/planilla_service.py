from collections import defaultdict

from app.integrations.siigo.pagos_api import obtener_planilla_siigo


async def obtener_planilla_de_pagos():
    pagina = 1
    resultados = []
    while True:
        response = await obtener_planilla_siigo(
            params={"page": pagina, "page_size": 100}
        )
        data = response.get("data", {})
        items = data.get("results", [])

        if not items:
            break
        resultados.extend(items)
        pagina += 1
    return resultados


def formatear_planilla_de_pagos(planilla):
    planilla.sort(key=lambda x: x.get("provider", {}).get("name", ""))
    planilla = agrupar_por_proveedor(planilla)
    return planilla


def agrupar_por_proveedor(planilla):
    proveedores = defaultdict(list)
    proveedores = defaultdict(lambda: {"facturas": [], "total": 0})
    total_general = 0
    for factura in planilla:
        if factura["due"]["balance"] and factura["provider"]["name"] not in VETADOS:
            nombre = factura["provider"]["name"]
            balance = factura["due"]["balance"]

            proveedores[nombre]["facturas"].append(factura)
            proveedores[nombre]["total"] += balance

            total_general += balance
    return proveedores, total_general


VETADOS = {
    "SILVERAGRO SAS",
    "SAMSUNG ELECTRONICS COLOMBIA S.A",
    "ITALCOL S.A",
    "CONTEGRAL S.A.S",
    "DOOIT SAS",
    "SIIGO S.A. S",
    "Davivienda",
    "ALFONSO ALIRIO ORTIZ MUÑOZ",
    "LAURA GABRIELA OSORIO VALDERRAMA",
    "EDWIN JULIAN LOPEZ TORRES",
    "PABLO ANDRES MURCIA FIGUEROA",
    "BRAYAN ROLDAN GARCIA BERMUDEZ",
    "ESNEDA HERNANDEZ ROSERO",
    "JUAN CARLOS ROJAS AGREDO",
    "NICTOR FERNANDO MAJE PEÑA",
}
