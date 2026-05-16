from pydantic import BaseModel


class FilaCierre(BaseModel):
    orden: int
    fecha: str
    numero: str
    cliente: str

    efectivo: float = 0
    banco: float = 0
    credito: float = 0
    cartera: float = 0
    metodo: str = ""
