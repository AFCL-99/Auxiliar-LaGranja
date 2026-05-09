from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.procesarFacturaCompra import procesar_preview_factura
from app.utils import generarHtml
from app.utils.temp_store import temp_data
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/compra", tags=["compra"])

@router.post("/preview", response_class=HTMLResponse)
async def preview_factura(file: UploadFile = File(...)):

    id_proceso, data = procesar_preview_factura(
        file,
        temp_data
    )

    html = generarHtml.generar_tabla_html(
        data,
        id_proceso
    )

    return html

@router.get("/preview", response_class=HTMLResponse)
def ver_preview(id_proceso: str):

    data = temp_data.get(id_proceso)

    if not data:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return generarHtml.generar_tabla_html(data, id_proceso)