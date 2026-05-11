from app.repositories.preview_repository import get_preview, save_preview
from app.services.analisis.analisis_precios_service import analizar_factura
from app.services.compra.buscar_service import buscar_factura_por_numero
from app.services.compra.crear_service import crear_factura_service
from app.views.compra_view import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Form, UploadFile, File, Request
from app.services.compra.preview_service import procesar_preview

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
