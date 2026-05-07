from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from app.services.siigo_api import crear_factura_desde_cotizacion, obtener_fecha_vencimiento

router = APIRouter(prefix="/cotizacion", tags=["cotizacion"])

@router.post("/facturar", response_class=HTMLResponse)
def facturar(numero: int = Form(...), tipo_vencimiento: str = Form(...)):

    fecha_vencimiento = obtener_fecha_vencimiento(tipo_vencimiento)

    resp = crear_factura_desde_cotizacion(numero, fecha_vencimiento)

    factura = resp.get("name")

    url_siigo = f"https://qbo.siigo.com/#/invoices/{resp.get('id')}"

    return f"""
    <html>
        <body>
            <h2>✅ Factura creada correctamente</h2>

            <p><strong>Factura:</strong> {factura}</p>

            <p>
                <a href="{url_siigo}" target="_blank">
                    🔗 Ver factura en Siigo
                </a>
            </p>

            <br><br>

            <a href="/">⬅ Volver</a>
        </body>
    </html>
    """