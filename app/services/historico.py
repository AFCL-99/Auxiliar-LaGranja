import pandas as pd

def obtener_precio_historico(codigo, factura_actual):

    df = cargar_historico()

    codigo_buscado = limpiar_codigo(codigo)
    df_filtrado = df[
        (df["codigo_limpio"] == codigo_buscado) &
        (df["comprobante"] != f"FC-1-{factura_actual}")
    ].sort_values(by="fecha", ascending=False)


    if df_filtrado.empty:
        return {
            "precio": 0,
            "factura": "",
            "fecha": None
        }

    df_filtrado = df_filtrado.sort_values(by="fecha", ascending=False)

    ultimo = df_filtrado.iloc[0]
    return {
        "precio": ultimo["precio"],
        "factura": ultimo["comprobante"],
        "fecha": ultimo["fecha"]
    }
_df_cache = None



def limpiar_codigo(valor):
    return str(valor).replace("C-", "").strip()


def parsear_numero(valor):
    if pd.isna(valor):
        return 0
    try:
        return float(str(valor).replace(",", "."))
    except:
        return 0


def cargar_historico():
    global _df_cache

    if _df_cache is None:
        df = pd.read_excel("app/data/consolidado.xlsx")
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        df["codigo_limpio"] = df["codigo"].apply(limpiar_codigo)
        df["precio"] = df["precio_unitario"].apply(parsear_numero)
        df["fecha"] = pd.to_datetime(df["fecha_elaboracion"], errors="coerce")

        _df_cache = df
    return _df_cache