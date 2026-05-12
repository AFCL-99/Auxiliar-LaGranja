import re

from app.providers.base import BaseProvider
from app.schemas.compra import FacturaCompra, Producto


class TamayoPolancoProvider(BaseProvider):

    proveedor = "TAMAYO POLANCO"

    def detect(self, text: str) -> bool:
        text = text.lower()
        return "nit 901987380" in text

    def extraer_factura(self, text: str):
        match = re.search(
            r"factura\s+electr[oó]nica\s+de\s+venta\s+([a-zA-Z]+)\s*-\s*(\d+)",
            text,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("No se pudo extraer la factura de Tamayo Polanco")

        prefijo = match.group(1).upper()
        numero = match.group(2)

        return f"{prefijo}-{numero}"

    def procesar(self, text: str) -> FacturaCompra:
        lineas = [linea.strip() for linea in text.split("\n") if linea.strip()]

        items = []

        for linea in lineas:
            producto = self._parsear_producto(linea)

            if producto:
                items.append(producto)

        return FacturaCompra(
            proveedor=self.proveedor,
            numeroFactura=self.extraer_factura(text),
            items=items,
            retefuente=True,
        )

    def _parsear_producto(self, linea: str):

        linea = self._normalizar_espacios(linea)

        patron = re.search(
            r"^\d+\s+"  # índice factura
            r"([0-9A-Za-z-]+)\s+"  # código proveedor
            r"(.+?)\s+"  # descripción
            r"(\d+(?:[.,]\d+)?)\s+"  # cantidad
            r"([a-zA-Z]+)\s+"  # unidad
            r"\$?\s*([\d,]+\.\d{2})\s+"  # precio unitario
            r"iva\s+(\d+(?:[.,]\d+)?)%\s+"  # IVA
            r"\$?\s*([\d,]+\.\d{2})\s+"  # subtotal
            r"\$?\s*([\d,]+\.\d{2})",  # total
            linea,
            re.IGNORECASE,
        )

        if not patron:
            return None

        codigo = patron.group(1)
        cantidad = self._numero(patron.group(3))
        precio = self._moneda_us(patron.group(5))
        iva = self._porcentaje(patron.group(6))

        return Producto(
            codigo=codigo,
            cantidad=cantidad,
            valorUnitario=precio,
            descuento=0,
            iva=iva,
        )

    def _numero(self, valor: str) -> float:
        return float(valor.replace(",", "."))

    def _porcentaje(self, valor: str) -> float:
        return float(valor.strip().replace("%", "").replace(",", "."))

    def _moneda_us(self, valor: str) -> float:
        """
        Convierte:
        $220,952.00 -> 220952.0
        """
        return float(valor.replace("$", "").replace(",", "").strip())

    def _normalizar_espacios(self, texto: str) -> str:
        return re.sub(r"\s+", " ", texto).strip()
