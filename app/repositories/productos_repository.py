from typing import List
import pandas as pd
from app.schemas.compra import Producto


def cargar_maestro_productos()->pd.DataFrame:
    df = pd.read_excel("app/data/productos.xlsx")

    df["codigo_proveedor"] = (
        df["codigo_proveedor"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return df

def mapear_productos(productos : List[Producto],df_productos: pd.DataFrame) -> List[Producto]:
    for producto in productos:
        codigo = producto.codigo.strip().upper()

        match = df_productos[
            df_productos["codigo_proveedor"].astype(str).str.upper() == codigo
        ]
        if not match.empty:
            productoDF = match.iloc[0]
            producto.descripcion = productoDF["nombre"]
            producto.codigo_Siigo = productoDF["codigo_siigo"]

    return productos
