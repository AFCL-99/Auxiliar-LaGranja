from abc import ABC, abstractmethod

from app.schemas.compra import FacturaCompra


class BaseProvider(ABC):
    @abstractmethod
    def detect(self, text: str) -> bool:
        pass

    @abstractmethod
    def procesar(self, text: str) -> FacturaCompra:
        pass

    @abstractmethod
    def extraer_factura(self, text: str):
        pass

    def transformar_pacas(self, codigo: str, cantidad: float, precioUnitario: float):
        unidades_por_paca = CONVERSIONES.get(codigo, 1)
        unidades = cantidad * unidades_por_paca
        valor_total = cantidad * precioUnitario
        precio_real = valor_total / unidades if unidades else 0

        return unidades, precio_real


CONVERSIONES = {
    # CONTEGRAL
    "592561": 15,
    "592861": 15,
    "592360": 15,
    "592460": 15,
    "521462": 6,
    "521362": 6,
    "592139": 3,
}
