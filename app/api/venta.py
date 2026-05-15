from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.services.ventas.cotizacion_service import buscar_cotizacion_por_numero
from app.services.ventas.facturacion_service import crear_facturaVenta_service

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
