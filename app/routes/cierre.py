from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import datetime
from app.services.siigo_cierre import obtener_cierre
from app.services.auth_service import get_token
from app.utils.generarHtml import generar_tabla_cierre

router = APIRouter(prefix="/cierre", tags=["cierre"])

@router.get("/", response_class=HTMLResponse)
def ver_cierre():

    fecha = str(datetime.date.today()-datetime.timedelta(days=0))

    token = get_token()

    data = obtener_cierre(token, fecha)

    html = generar_tabla_cierre(data)

    return html