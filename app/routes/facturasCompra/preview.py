from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services import leerPdf, leerExcel
from app.services.factura_service import calcular_totales_factura, detectar_y_procesar
from app.services.procesarFacturaCompra import procesar_preview_factura
from app.utils import generarHtml
import shutil
import os
import uuid
from app.utils.temp_store import temp_data

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
        return """
        <h2>Proceso no encontrado</h2>
        <p>La previsualización expiró o no existe.</p>
        <a href="/">Volver al inicio</a>
        """

    return generarHtml.generar_tabla_html(data, id_proceso)