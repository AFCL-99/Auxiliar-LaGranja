from fastapi import APIRouter, Form

from app.services.factura_service import actualizar_bodega_factura

router = APIRouter()

@router.post("/compra/trasladar")
def trasladar(
    id_factura: int = Form(...),
    nueva_bodega: int = Form(...)
):
    return actualizar_bodega_factura(id_factura, nueva_bodega)