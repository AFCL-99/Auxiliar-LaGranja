from pydantic import BaseModel


class SuccessResponseCompra(BaseModel):
    sucess: bool = True
    factura_id: int
    respuestaJson: str


class ErrorResponse(BaseModel):
    sucess: bool = False
    mensaje: str


class SiigoAPIError(Exception):

    def __init__(self, status_code: int, detail: dict):

        self.status_code = status_code
        self.detail = detail
