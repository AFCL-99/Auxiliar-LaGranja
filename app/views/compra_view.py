from fastapi.templating import Jinja2Templates
from app.utils.numbers import formatear_moneda, formatear_procentaje

templates = Jinja2Templates(directory="app/templates")

templates.env.filters["moneda"] = formatear_moneda
templates.env.filters["porcentaje"] = formatear_procentaje
