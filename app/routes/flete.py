from fastapi import APIRouter, Form
from app.services.flete_service import existe_flete, obtener_fletes_existentes
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/flete", tags=["flete"])
@router.get("/crear", response_class=HTMLResponse)
def crear_flete(factura: str):

    if existe_flete(factura):
        return {"error": "Ya existe ajuste de flete para esta factura"}

    #journal = construir_journal(factura)
    #response = enviar_journal(journal)

    return ""

@router.get("/")
def listar_fletes():
    return obtener_fletes_existentes()