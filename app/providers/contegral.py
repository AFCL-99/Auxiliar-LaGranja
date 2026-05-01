import math
import re
def limpiar_numero(valor):
    valor = valor.replace("$", "").replace(",", "").strip()
    return float(valor) if valor else 0.0

def procesar(texto):
    
    texto = texto.lower()
    
    bloque_propios, bloque_mandato = separar_bloques_contegral(texto)
    
    items_propios = extraer_items_contegral(bloque_propios)
    items_mandato = extraer_items_contegral(bloque_mandato)

    return {
            "proveedor": "CONTEGRAL",
            "factura_id": extraer_factura(texto),
            "items": items_propios + items_mandato
        }

def extraer_items_contegral(bloque):
    items = []
    lineas = bloque.split("\n")
    
    for linea in lineas:
        linea = linea.strip()
        
        if "descripcion" in linea.lower():
            continue
        
        if not re.match(r'^\d+\s+\d+', linea):
            continue
        
        try:
            partes = linea.split()
            
            nro = partes[0]
            codigo = partes[1]
            
            # 🔥 manejar IVA con % separado
            if partes[-1] == "%":
                iva = float(partes[-2])
                idx = -2
            else:
                iva = float(partes[-1].replace("%", ""))
                idx = -1
            
            total_factura = limpiar_numero(partes[idx - 1])
            descuento = limpiar_numero(partes[idx - 2])
            precio_unitario = limpiar_numero(partes[idx - 3])
            bultos = float(partes[idx - 5])
            total_calculado = bultos * precio_unitario
            descuento = math.floor(total_calculado - total_factura+0.5)
            
            # 🚫 filtrar líneas inútiles
            if precio_unitario == 0 and bultos == 0:
                continue
            
            bultos, precio_unitario = transformar_pacas(codigo,bultos,precio_unitario)

            items.append({
                "nro": int(nro),
                "codigo": codigo,
                "cantidad": bultos,
                "precio": formatear_precio(precio_unitario),
                "descuento": descuento,
                "iva": iva
            })
        
        except Exception as e:
            print("Error procesando:", linea)
            print(e)
    
    return items


def extraer_factura(texto):
    patron = r"(FGN)\s*0*(\d+)"

    match = re.search(patron, texto.upper())

    if match:
        prefijo = match.group(1)
        numero = match.group(2)

        return f"{prefijo}-{numero}"

    return None

def separar_bloques_contegral(texto):
    
    partes = texto.split("ingresos por mandato")
    
    concentrado = partes[0]
    mascotas = partes[1] if len(partes) > 1 else ""
    
    return concentrado, mascotas

CONVERSIONES = {
    "592561":15,
    "592861":15,
    "592360":15,
    "592460":15,
    "521462":6,
    "521362":6

}
def transformar_pacas(codigo, cantidad, precioUnitario):
    unidades_por_paca = CONVERSIONES.get(codigo,1)
    unidades = cantidad * unidades_por_paca
    valor_total = cantidad * precioUnitario
    precio_real = valor_total/unidades if unidades else 0

    return unidades, precio_real

from decimal import Decimal, ROUND_HALF_UP

def formatear_precio(valor):
    return float(
        Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )