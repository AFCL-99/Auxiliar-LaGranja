import json

from app.integrations.siigo.pagos_api import obtener_planilla_siigo


async def obtener_planilla_de_pagos():
    response = await obtener_planilla_siigo(params=None)
    print(json.dumps(response, indent=4))
    planilla = response.get("data", {}).get("results", [])

    print(json.dumps(planilla, indent=4))
    return planilla


def formatear_planilla_de_pagos(planilla):
    pass
