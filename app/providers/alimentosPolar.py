import re

from app.providers.base import BaseProvider
from app.schemas.compra import FacturaCompra, Producto


class AlimentosPolarProvider(BaseProvider):

    proveedor = "ALIMENTOS POLAR"

    def detect(self, text: str) -> bool:

        text = text.lower()

        return "alimentos polar" in text or "ffnz" in text

    def procesar(self, text: str) -> FacturaCompra:

        lineas = [linea.strip() for linea in text.split("\n") if linea.strip()]

        items = []

        for linea in lineas:

            if not re.match(r"^[a-zA-Z]\d{3,}", linea):
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
            r"nica de venta no.ffnz\s*(\d+)",
            text,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("No se pudo extraer la factura")

        return f"FFNZ-{match.group(1)}"

    def _parsear_producto(self, linea: str) -> Producto | None:

        try:

            limpia = linea.replace("$", "").replace(".", "").replace(",", ".")

            partes = limpia.split()

            codigo = partes[0]

            numeros = [float(p) for p in partes if self._es_numero(p)]

            if len(numeros) < 8:
                return None

            cantidad = numeros[-9]

            precio_unitario = numeros[-6]

            descuento = numeros[-4]

            iva = numeros[-2]

            return Producto(
                codigo=codigo,
                cantidad=cantidad,
                valorUnitario=precio_unitario,
                descuento=descuento,
                tipoDescuento=False,
                iva=iva,
            )

        except Exception as e:

            print(f"Error procesando línea: {linea}", e)

            return None

    def _es_numero(self, valor: str) -> bool:

        return bool(re.match(r"^\d+(\.\d+)?$", valor))
