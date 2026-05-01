from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.siigo_api import obtener_factura
from app.services.analisis_precio import analizar_factura
from app.services.historico import obtener_precio_historico
from app.views.html_analisis import generar_html_analisis

router = APIRouter(prefix="/analisis", tags=["analisis"])


@router.get("/factura", response_class=HTMLResponse)
def analizar(numero: str):

    try:
        factura = obtener_factura(numero)

        resultado = analizar_factura(
            factura,
            obtener_precio_historico
        )
        html = generar_html_analisis(resultado)

        return html

    except Exception as e:
        return f"<h2>Error</h2><p>{str(e)}</p>"