import pandas as pd


def cargar_clientes():
    df = pd.read_excel("app/data/Clientes.xlsx")

    df["ID"] = df["ID"].astype(str).str.strip()

    return df


def obtener_nombre_cliente(identificacion, df_clientes, cache):
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
