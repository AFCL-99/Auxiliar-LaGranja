import re

from app.providers.base import BaseProvider
from app.schemas.compra import FacturaCompra, Producto


class ItalcolDeOccidenteProvider(BaseProvider):

    proveedor = "ITALCOL DE OCCIDENTE SA"

    def detect(self, text: str) -> bool:

        text = text.lower()

        return "nit: 891304762-2" in text

    def procesar(self, text: str) -> FacturaCompra:

        lineas = [linea.strip() for linea in text.split("\n") if linea.strip()]

        items = []

        for linea in lineas:

            linea = linea.lower()

            if not re.match(r"^[a-zA-Z]?\d{3,}\s+", linea):
                continue

            producto = self._parsear_producto(linea)

            if producto:
                items.append(producto)

        return FacturaCompra(
            proveedor=self.proveedor,
            numeroFactura=self.extraer_factura(text),
            items=items,
        )

    def extraer_factura(self, text: str) -> str:

        match = re.search(
            r"\b(\d{3}[a-zA-Z])\s*-?\s*(\d{4,})\b",
            text,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("No se pudo extraer el número de factura")

        prefijo = match.group(1).upper()

        numero = match.group(2)

        return f"{prefijo}-{numero}"

    def _parsear_producto(self, linea: str) -> Producto | None:

        try:
            patron = re.search(
                r"^([a-zA-Z]?\d{3,})\s+.*?\s+"
                r"(\d+(?:[.,]\d+)?)\s+"  # cantidad
                r"([a-zA-Z]+)\s+"  # unidad
                r"(\d+(?:[.,]\d+)?)\s+"  # kilos
                r"\$?\s*([\d.,]+)\s+"  # precio unitario
                r"\$?\s*([\d.,]+)\s+"  # subtotal
                r"(\d+(?:[.,]\d+)?)\s*%?",  # IVA
                linea,
            )

            if not patron:
                return None

            codigo = patron.group(1)

            cantidad = self._numeroItalcolOccidente(patron.group(2))

            precio_unitario = self._numeroItalcolOccidente(patron.group(5))

            iva = self._porcentaje(patron.group(7))

            descuento = round(precio_unitario * cantidad * 0.02, 2)

            cantidad, precio_unitario = self.transformar_pacas(
                codigo, cantidad, precio_unitario
            )

            return Producto(
                codigo=codigo,
                cantidad=cantidad,
                valorUnitario=precio_unitario,
                descuento=descuento,
                tipoDescuento=True,
                iva=iva,
            )

        except Exception as e:

            print(f"Error procesando línea: {linea}", e)

            return None

    def _numeroItalcolOccidente(self, valor: str) -> float:

        valor = valor.strip().replace("$", "").replace(" ", "")
        if "." in valor and "," not in valor:
            return float(valor.replace(".", ""))

        if "," in valor:
            return float(valor.replace(",", "."))
        return float(valor)
