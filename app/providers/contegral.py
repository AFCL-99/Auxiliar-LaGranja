from typing import List

from app.providers.base import BaseProvider
import re
import math

from app.schemas.compra import FacturaCompra, Producto
from app.utils.numbers import formatear_precio, limpiar_numero


class contegralProvider(BaseProvider):
    def detect(self, text) -> bool:
        return "890901271-5" in text.upper()

    def extraer_factura(self, texto) -> str:
        patron = r"(FGN)\s*0*(\d+)"

        match = re.search(patron, texto.upper())

        if match:
            prefijo = match.group(1)
            numero = match.group(2)

            return f"{prefijo}-{numero}"

        return ""

    def procesar(self, texto: str):
        texto = texto.lower()

        bloque_propios, bloque_mandato = self.separar_bloques_contegral(texto)

        items_propios = self.extraer_items_contegral(bloque_propios)
        items_mandato = self.extraer_items_contegral(bloque_mandato)
        items = items_propios + items_mandato
        return FacturaCompra(
            proveedor="CONTEGRAL",
            numeroFactura=self.extraer_factura(texto),
            items=items,
        )

    def separar_bloques_contegral(self, texto):

        partes = texto.split("ingresos por mandato")

        concentrado = partes[0]
        mascotas = partes[1] if len(partes) > 1 else ""

        return concentrado, mascotas

    def extraer_items_contegral(self, bloque: str) -> List[Producto]:

        productos: List[Producto] = []

        for linea in bloque.splitlines():

            linea = linea.strip()
            if not linea:
                continue

            # Ignorar encabezados
            if "descripcion" in linea.lower():
                continue

            # Solo líneas que parecen productos
            if not re.match(r"^\d+\s+\d+", linea):
                continue

            try:

                # Reparar IVA pegado al total
                linea = re.sub(r"(\$\d[\d,]*\.\d{2})(\d+\.\d{2}\s*%)", r"\1 \2", linea)

                partes = linea.split()

                codigo = partes[1]

                # -----------------------------
                # IVA
                # -----------------------------
                if partes[-1] == "%":
                    iva = float(partes[-2])
                    idx_iva = -2
                else:
                    iva = float(partes[-1].replace("%", ""))
                    idx_iva = -1

                # -----------------------------
                # Valores numéricos
                # -----------------------------
                total_factura = limpiar_numero(partes[idx_iva - 1])
                precio_unitario = limpiar_numero(partes[idx_iva - 3])

                # idx_iva -4 suele ser cantidad menor/empaque
                cantidad = float(partes[idx_iva - 5])

                if cantidad == 0 or precio_unitario == 0:
                    continue

                cantidad, precio_unitario = self.transformar_pacas(
                    codigo, cantidad, precio_unitario
                )
                subtotal = cantidad * precio_unitario

                descuento = math.floor(subtotal - total_factura + 0.5)

                descuento = max(descuento, 0)

                producto = Producto(
                    codigo=codigo,
                    cantidad=cantidad,
                    valorUnitario=formatear_precio(precio_unitario),
                    descuento=descuento,
                    iva=iva,
                )
                productos.append(producto)

            except Exception as e:

                print("\nError procesando línea:")
                print(linea)
                print(type(e).__name__, e)

        return productos
