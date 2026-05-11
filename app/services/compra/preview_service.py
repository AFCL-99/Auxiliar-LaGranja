import uuid
import os
import shutil

from fastapi import UploadFile
from app.repositories.productos_repository import (
    cargar_maestro_productos,
    mapear_productos,
)
from app.schemas.compra import PreviewProceso
from app.services.documentos.pdf_service import extraer_texto_pdf
from app.services.compra.provider_detector import detectar_provedor

preview_cache = {}


async def procesar_preview(file: UploadFile):
    df = cargar_maestro_productos()
    process_id = str(uuid.uuid4())
    ruta_temp = f"temp_{file.filename}"

    with open(ruta_temp, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        texto = extraer_texto_pdf(ruta_temp)

        provider = detectar_provedor(texto)

        factura = provider.procesar(texto)
        factura.items = mapear_productos(factura.items, df)
        preview_cache[process_id] = factura

        return PreviewProceso(process_id=process_id, factura=factura)
    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)
