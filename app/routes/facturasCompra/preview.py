from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services import leerPdf, leerExcel
from app.services.factura_service import calcular_totales_factura, detectar_y_procesar
from app.utils import generarHtml
import shutil
import os
import uuid
from app.utils.temp_store import temp_data
from datetime import date

router = APIRouter(prefix="/compra", tags=["compra"])

@router.post("/preview", response_class=HTMLResponse)
async def preview_factura(file: UploadFile = File(...)):
    id_proceso = str(uuid.uuid4())
    ruta_temp = f"temp_{file.filename}"

    with open(ruta_temp, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    texto = leerPdf.extraer_texto_pdf(ruta_temp)
    data_proveedor = detectar_y_procesar(texto)
    items = data_proveedor["items"]
    id_factura = data_proveedor["factura_id"]
    proveedor = data_proveedor["proveedor"]
    print(proveedor)
    df = leerExcel.cargar_maestro_productos("app/data/productos.xlsx")
    items = leerExcel.mapear_productos(items, df)
    totales = calcular_totales_factura(items)

    temp_data[id_proceso] = {
        "factura_id": id_factura,
        "items": items,
        "fecha": date.today().strftime("%Y-%m-%d"),
        "proveedor": proveedor,
        "totales": totales
    }

    os.remove(ruta_temp)

    html = generarHtml.generar_tabla_html(temp_data[id_proceso], id_proceso)

    return html

@router.get("/preview", response_class=HTMLResponse)
def formulario():
    return """
    <html>
        <body>
            <h2>Subir factura</h2>
            <form action="/compra/preview" method="post" enctype="multipart/form-data">
                <input type="file" name="file"/>
                <button type="submit">Procesar</button>
            </form>
        </body>
    </html>
    """
