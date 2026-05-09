from datetime import datetime, timedelta

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from app.services.siigo_api import crear_factura_desde_cotizacion

router = APIRouter(prefix="/cotizacion", tags=["cotizacion"])

@router.post("/facturar", response_class=HTMLResponse)
def facturar(numero: int = Form(...), tipo_vencimiento: str = Form(...)):

    fecha_vencimiento = obtener_fecha_vencimiento(tipo_vencimiento)

    resp = crear_factura_desde_cotizacion(numero, fecha_vencimiento)

    factura = resp.get("name")

    return f"""
    <html>
        <body>
            <h2>✅ Factura creada correctamente</h2>

            <p><strong>Factura:</strong> {factura}</p>

            <br><br>

            <a href="/">⬅ Volver</a>
        </body>
    </html>
    """

def obtener_fecha_vencimiento(tipo):

    hoy = datetime.now()

    if tipo == "hoy":
        return hoy.strftime("%Y-%m-%d")

    elif tipo == "15":
        return (hoy + timedelta(days=15)).strftime("%Y-%m-%d")

    elif tipo == "fin_mes":
        siguiente_mes = hoy.replace(day=28) + timedelta(days=4)
        ultimo_dia = siguiente_mes - timedelta(days=siguiente_mes.day)

        return ultimo_dia.strftime("%Y-%m-%d")