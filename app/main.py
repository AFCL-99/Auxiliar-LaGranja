from fastapi import FastAPI
from app.routes.facturasCompra import actualizar, preview
from app.routes.facturasCompra import crear
from app.routes import cierre, facturar, flete
from app.routes import analisis, index
app = FastAPI(
    title="Sistema SIIGO",
    description="Automatización de facturas y procesos contables",
    version="1.0.0"
)
    
# incluir rutas
app.include_router(index.router)
app.include_router(preview.router)
app.include_router(crear.router)
app.include_router(analisis.router)
app.include_router(cierre.router)
app.include_router(flete.router)
app.include_router(facturar.router)
app.include_router(actualizar.router)