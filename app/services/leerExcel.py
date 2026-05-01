import pandas as pd

def cargar_maestro_productos(ruta_excel):
    df = pd.read_excel(ruta_excel)
    # asegurar tipos
    df["codigo_proveedor"] = (
        df["codigo_proveedor"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return df

def mapear_productos(items, df_productos):
    
    resultado = []
    
    for item in items:
        codigo = item["codigo"].strip().upper()
        
        match = df_productos[df_productos["codigo_proveedor"] == codigo]
        
        if not match.empty:
            producto = match.iloc[0]
            
            item["nombre"] = producto["nombre"]
            item["codigo_siigo"] = producto["codigo_siigo"]
            item["encontrado"] = True
        else:
            item["nombre"] = "NO ENCONTRADO"
            item["codigo_siigo"] = None
            item["encontrado"] = False
        
        resultado.append(item)
    
    return resultado

def cargar_clientes(ruta):
    df = pd.read_excel(ruta)

    df["ID"] = df["ID"].astype(str).str.strip()

    return df

def mapear_clientes(identificacion,df_clientes,cache):
    identificacion = str(identificacion).strip()

    if identificacion in cache:
        return cache[identificacion]
    
    match = df_clientes[df_clientes["ID"] == identificacion]
    if not match.empty:
        nombre = match.iloc[0]["Nombre"]
    else:
        nombre = identificacion

    cache[identificacion] = nombre

    return nombre