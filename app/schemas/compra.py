from pydantic import BaseModel
from typing import List


class Producto(BaseModel):
    codigo: str
    descripcion: str = "NO ENCONTRADO"
    cantidad: float
    valorUnitario: float
    descuento: float = 0
    tipoDescuento: bool = True
    iva: float = 0
    codigo_Siigo: str = "FER02"

    @property
    def subtotal(self):
        return round(self.cantidad * self.valorUnitario, 2)

    @property
    def precioReal(self):
        descuento_unitario = self.descuentoReal / self.cantidad if self.cantidad else 0
        return round(self.valorUnitario - descuento_unitario, 2)

    @property
    def descuentoReal(self):
        if self.tipoDescuento:
            return self.descuento
        return self.subtotal * (self.descuento / 100)

    def mostrarProducto(self):
        subtotal = self.subtotal

        total_descuento = subtotal * (self.descuento / 100)
        base = subtotal - total_descuento

        total_iva = base * (self.iva / 100)
        total = base + total_iva

        return (
            f"Producto: {self.codigo}\n"
            f"--Cantidad: {self.cantidad}\n"
            f"--Valor unitario: ${self.valorUnitario:,.2f}\n"
            f"--Subtotal: ${self.subtotal:,.2f}\n"
            f"--Descuento: {self.descuento}% (-${total_descuento:,.2f})\n"
            f"--IVA: {self.iva}% (+${total_iva:,.2f})\n"
            f"--Total: ${total:,.2f}"
        )


class FacturaCompra(BaseModel):
    proveedor: str
    numeroFactura: str
    items: List[Producto]

    @property
    def calcularSubtotal(self) -> float:
        subtotal = 0
        for item in self.items:
            subtotal += item.subtotal
        return subtotal

    @property
    def calcularDescuentos(self) -> float:
        descuento = 0
        for item in self.items:
            descuento += item.descuentoReal
        return descuento

    @property
    def calcularIvaTotal(self) -> float:
        totalIva = 0
        for item in self.items:
            precioItem = round(item.precioReal * item.cantidad, 2)
            totalIva += round(precioItem * item.iva / 100, 2)
        return totalIva

    @property
    def total(self) -> float:
        return self.calcularSubtotal + self.calcularIvaTotal - self.calcularDescuentos

    def separar_factura_id(self):
        prefijo, numero = self.numeroFactura.split("-")

        return prefijo, numero


class PreviewProceso(BaseModel):
    process_id: str
    factura: FacturaCompra
