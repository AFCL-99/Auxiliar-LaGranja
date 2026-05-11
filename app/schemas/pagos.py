from pydantic import BaseModel


class PagoOCR(BaseModel):
    fecha: str
    valor: float
    pagodoA: str
    banco: str
