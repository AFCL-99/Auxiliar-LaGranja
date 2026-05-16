from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.repositories.preview_repository import get_preview, save_preview
from app.services.analisis.analisis_precios_service import analizar_factura
from app.services.compra.buscar_service import buscar_factura_por_numero
from app.services.compra.crear_service import crear_factura_service
from app.services.compra.preview_service import procesar_preview
from app.services.pagos.planilla_service import (
    formatear_planilla_de_pagos,
    obtener_planilla_de_pagos,
)
from app.views.compra_view import templates

router = APIRouter(prefix="/compra", tags=["compra"])


@router.post("/preview", response_class=HTMLResponse)
async def preview_factura(request: Request, file: UploadFile = File(...)):

    resultado = await procesar_preview(file)
    save_preview(resultado)
    return templates.TemplateResponse(
        request=request,
        name="compra_preview.html",
        context={"factura": resultado.factura, "process_id": resultado.process_id},
    )


@router.get("/preview/{process_id}", response_class=HTMLResponse)
def cargar_preview(request: Request, process_id: str):

    factura = get_preview(process_id)
    if not factura:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="compra_preview.html",
        context={"factura": factura, "process_id": process_id},
    )


@router.post("/crear")
async def crear_factura(process_id: str = Form(...)):
    factura = get_preview(process_id)

    if not factura:
        return RedirectResponse(url="/", status_code=303)
    return await crear_factura_service(process_id)


@router.get("/analizar", response_class=HTMLResponse)
async def analizar(request: Request, numero: str):

    factura = await buscar_factura_por_numero(numero)
    if not factura:
        return RedirectResponse(url="/", status_code=303)
    analisis = analizar_factura(factura)
    return templates.TemplateResponse(
        request=request,
        name="compra_analisis.html",
        context={"items": analisis.get("items")},
    )


@router.get("/planillar", response_class=HTMLResponse)
async def planillaPagos(request: Request):

    planilla = await obtener_planilla_de_pagos()
    if not planilla:
        return RedirectResponse(url="/", status_code=303)
    planilla_formateada, total_general = formatear_planilla_de_pagos(planilla)
    return templates.TemplateResponse(
        request=request,
        name="planilla_pagos.html",
        context={"planilla": planilla_formateada, "total_general": total_general},
    )
