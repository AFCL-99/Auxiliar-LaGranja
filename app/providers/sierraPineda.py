import re
from app.providers.base import BaseProvider
from app.schemas.compra import FacturaCompra, Producto


class SierraPinedaProvider(BaseProvider):

    proveedor = "SIERRA PINEDA"

    def detect(self, text: str) -> bool:
        text = text.lower()
        return "890705018 - 8" in text

    def extraer_factura(self, text: str):
        match = re.search(
            r"factura\s+electr[oó]nica\s+de\s+venta\s+([a-zA-Z]+)[-\s]?(\d+)",
            text,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("No se pudo extraer el número de factura")

        prefijo = match.group(1).upper()
        numero = match.group(2)

        return f"{prefijo}-{numero}"

    def procesar(self, text: str) -> FacturaCompra:
        lineas = [linea.strip() for linea in text.split("\n") if linea.strip()]

        items = []
        buffer = ""

        for linea in lineas:

            # Nueva línea de producto
            if re.match(r"^\d{4,6}\s+", linea):
                if buffer:
                    producto = self._parsear_producto(buffer)
                    if producto:
                        items.append(producto)

                buffer = linea

            else:
                # Continuación del nombre o código de barras
                if buffer:
                    buffer += " " + linea

        # Procesar último producto acumulado
        if buffer:
            producto = self._parsear_producto(buffer)
            if producto:
                items.append(producto)

        return FacturaCompra(
            proveedor=self.proveedor,
            numeroFactura=self.extraer_factura(text),
            items=items,
        )

    def _parsear_producto(self, linea: str):

        linea = self._normalizar_espacios(linea)

        patron = re.search(
            r"^(\d{4,6})\s+"  # código
            r"(.+?)\s+"  # descripción
            r"(\d+(?:[.,]\d+)?)\s+"  # unidades por empaque
            r"([a-zA-Z]+)\s+"  # unidad medida
            r"(?:(\d+(?:[.,]\d+)?)\s+)?"  # pacas opcional
            r"(\d+(?:[.,]\d+)?)\s+"  # cantidad
            r"([\d.,]+)\s+"  # precio unitario
            r"(\d+(?:[.,]\d+)?)\s*%\s+"  # descuento %
            r"(\d+(?:[.,]\d+)?)\s*%\s+"  # IVA %
            r"([\d.,]+)\s+"  # precio neto
            r"([\d.,]+)",  # total
            linea,
            re.IGNORECASE,
        )

        if not patron:
            print(f"No se pudo parsear producto Sierra Pineda: {linea}")
            return None

        codigo = patron.group(1)

        cantidad = self._numero(patron.group(6))
        precio = self._numero(patron.group(7))
        descuento = self._porcentaje(patron.group(8))
        print(f"{patron.group(8)}->{descuento}")
        iva = self._porcentaje(patron.group(9))
        return Producto(
            codigo=codigo,
            cantidad=cantidad,
            valorUnitario=precio,
            descuento=descuento,
            tipoDescuento=False,
            iva=iva,
        )

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

    def _normalizar_espacios(self, texto: str) -> str:
        return re.sub(r"\s+", " ", texto).strip()
