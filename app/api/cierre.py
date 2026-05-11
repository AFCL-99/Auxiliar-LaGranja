from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.cierre.service import obtener_cierre
from app.views.compra_view import templates

router = APIRouter(prefix="/cierre", tags=["cierre"])


@router.get("/", response_class=HTMLResponse)
async def ver_cierre(request: Request):

    data = await obtener_cierre()
    if not data:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="compra_analisis.html",
        context={"filas": data},
    )
