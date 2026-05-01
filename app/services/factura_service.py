from app.providers import contegral, italcol, alimentosPolar, italcolDeOccidente, gabrica
from app.services.siigo_api import actualizar_factura_siigo

def detectar_y_procesar(texto):

    if "860,026,895-8" in texto:
        return italcol.procesar(texto)

    if "890901271-5" in texto:
        return contegral.procesar(texto)

    if "830.006.735-3" in texto:
        return alimentosPolar.procesar(texto)
    
    if "nit: 891304762-2" in texto:
        return italcolDeOccidente.procesar(texto)

    if "nit 800164767 - 6" in texto:
        return gabrica.procesar(texto)

    raise Exception("Proveedor no soportado")


def detectar_y_actualizar(id_factura: str, texto: str):

    items = detectar_y_procesar(texto)

    # 🔹 actualizar factura
    response = actualizar_factura_siigo(id_factura, items)

    return response