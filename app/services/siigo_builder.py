from app.services.siigo_builders import contegral, italcol, alimentosPolar, gabrica, italcolDeOccidente
BUILDERS = {
    "CONTEGRAL": contegral.construir,
    "ITALCOL": italcol.construir,
    "ALIMENTOS POLAR": alimentosPolar.construir,
    "GABRICA":gabrica.construir,
    "ITALCOL DE OCCIDENTE SA":italcolDeOccidente.construir
}

def construir_payload(data):
    
    proveedor = data.get("proveedor")

    if proveedor not in BUILDERS:
        raise Exception(f"Proveedor no soportado: {proveedor}")

    builder = BUILDERS[proveedor]

    return builder(data)