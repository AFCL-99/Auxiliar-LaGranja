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

    def _numero(self, valor: str) -> float:
        valor = valor.strip().replace("%", "")

        # Caso colombiano: 39,180 = 39180
        if "," in valor and "." not in valor:
            return float(valor.replace(",", ""))

        # Caso colombiano: 1.234.567,89
        if "." in valor and "," in valor:
            return float(valor.replace(".", "").replace(",", "."))

        return float(valor)

    def _porcentaje(self, valor: str) -> float:
        valor = valor.strip().replace("%", "").replace(",", ".")

        return float(valor)

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
    # ITALCOL DE OCCIDENTE
    "154506": 3,
    "151222": 4,
    "151239": 4,
    "154469": 4,
    "154452": 6,
    "150263": 6,
    "153356": 4,
    "153325": 6,
    "157330": 10,
    "154612": 20,
    "153141": 8,
    "154124": 4,
    "154131": 6,
    "154889": 10,
    "154858": 4,
    "157005": 6,
    "154974": 6,
    "157750": 4,
    "158191": 4,
    "158207": 3,
    "157958": 12,
    "157682": 6,
    "150737": 4,
    "156838": 20,
    "151031": 6,
    "151246": 4,
    "154667": 20,
    "153448": 6,
    "157036": 6,
    "157743": 6,
    "159143": 6,
    "155251": 3,
    "153053": 12,
    "153408": 12,
}
