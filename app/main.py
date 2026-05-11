from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import compra, index

app = FastAPI(
    title="Sistema SIIGO",
    description="Automatización de facturas y procesos contables",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(index.router)
app.include_router(compra.router)