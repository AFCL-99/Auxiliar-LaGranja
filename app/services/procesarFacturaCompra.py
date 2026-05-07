import uuid
import os
import shutil
from datetime import date

from app.services import leerPdf, leerExcel
from app.services.factura_service import calcular_totales_factura, detectar_y_procesar


def procesar_preview_factura(file, temp_data):
    id_proceso = str(uuid.uuid4())
    ruta_temp = f"temp_{file.filename}"

    with open(ruta_temp, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        texto = leerPdf.extraer_texto_pdf(ruta_temp)

        data_proveedor = detectar_y_procesar(texto)

        items = data_proveedor["items"]
        factura_id = data_proveedor["factura_id"]
        proveedor = data_proveedor["proveedor"]

        df = leerExcel.cargar_maestro_productos(
            "app/data/productos.xlsx"
        )

        items = leerExcel.mapear_productos(items, df)

        totales = calcular_totales_factura(items)

        hay_productos_no_encontrados = any(
            not item.get("encontrado", False)
            for item in items
        )

        temp_data[id_proceso] = {
            "factura_id": factura_id,
            "items": items,
            "fecha": date.today().strftime("%Y-%m-%d"),
            "proveedor": proveedor,
            "totales": totales,
            "hay_productos_no_encontrados": hay_productos_no_encontrados
        }

        return id_proceso, temp_data[id_proceso]

    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)