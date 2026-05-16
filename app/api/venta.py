from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.cierre.cierre_service import obtener_cierre_diario
from app.services.ventas.cotizacion_service import buscar_cotizacion_por_numero
from app.services.ventas.facturacion_service import crear_facturaVenta_service
from app.views.compra_view import templates

router = APIRouter(prefix="/venta", tags=["venta"])


@router.post("/crear")
async def crear_factura(
    request: Request, numero: str = Form(...), tipo_vencimiento: str = Form(...)
):
    cotizacion = await buscar_cotizacion_por_numero(numero)

    if not cotizacion.get("data"):
        print("Cotizacion no encontrada")
        return RedirectResponse(url="/", status_code=303)
    resultado = cotizacion.get("data")
    return await crear_facturaVenta_service(resultado, tipo_vencimiento)


@router.get("/cierre", response_class=HTMLResponse)
async def ver_cierre(request: Request):
    data = await obtener_cierre_diario()
    if not data:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="cierre_diario.html",
        context={"filas": data},
    )
