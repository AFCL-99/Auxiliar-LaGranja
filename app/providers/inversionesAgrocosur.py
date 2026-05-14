import re

from app.providers.base import BaseProvider
from app.schemas.compra import FacturaCompra, Producto
from app.utils.strings import normalizar_espacios


class InversionesAgrocosurProvider(BaseProvider):

    proveedor = "INVERSIONES AGROCOSUR"

    def detect(self, text: str) -> bool:
        return "900935276-3" in text

    def extraer_factura(self, text: str):
        match = re.search(r"\b\d+\s+([a-zA-Z]{2}\d{2})\s+(\d+)\b", text, re.IGNORECASE)

        if not match:
            raise ValueError("No se pudo extraer la factura de INVERSIONES AGROCOSUR")

        prefijo = match.group(1).upper()
        numero = match.group(2)

        return f"{prefijo}-{numero}"

    def procesar(self, text: str) -> FacturaCompra:
        items = []

        for linea in text.split("\n"):
            producto = self._parsear_producto(linea.strip())

            if producto:
                items.append(producto)

        return FacturaCompra(
            proveedor=self.proveedor,
            numeroFactura=self.extraer_factura(text),
            items=items,
        )

    def _parsear_producto(self, linea: str):

        linea = normalizar_espacios(linea)
        linea = self._normalizar_indice_codigo(linea)

        patron = re.search(
            r"^\d+\s+"
            r"(\d+)\s+"
            r"-\d+\s+"
            r"(.+?)\s+"
            r"(?:(0|5|19)\s+)?"
            r"(\d+(?:[.,]\d+)?)\s+"
            r"([\d.,]+)\s+"
            r"([\d.,]+)$",
            linea,
            re.IGNORECASE,
        )

        if not patron:
            return None

        codigo = patron.group(1)
        iva = self._numero(patron.group(3)) if patron.group(3) else 0
        cantidad = self._numero(patron.group(4))
        precio = self._moneda_colombiana(patron.group(5))

        return Producto(
            codigo=codigo,
            cantidad=cantidad,
            valorUnitario=precio,
            descuento=0,
            iva=iva,
        )

    def _numero(self, valor: str) -> float:
        return float(valor.replace(",", "."))

    def _moneda_colombiana(self, valor: str) -> float:
        """
        Convierte:
        30,429.00 -> 30429
        426,006.00 -> 426006
        """
        return float(valor.replace(",", "").strip())

    def _normalizar_indice_codigo(self, linea: str) -> str:
        """
        Corrige casos como:
        1018091 -003 producto...

        donde realmente es:
        10 18091 -003 producto...
        """

        match = re.match(r"^(\d{2})(\d{4,6})\s+(-\d{3})\s+(.+)$", linea)

        if match:
            indice = match.group(1)
            codigo = match.group(2)
            bodega = match.group(3)
            resto = match.group(4)

            return f"{indice} {codigo} {bodega} {resto}"

        return linea
