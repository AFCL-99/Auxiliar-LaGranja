from app.providers.contegral import contegralProvider
from app.providers.sierraPineda import SierraPinedaProvider

providers = [contegralProvider(), SierraPinedaProvider()]


def detectar_provedor(texto: str):
    for provider in providers:
        if provider.detect(texto):
            return provider

    raise Exception("Proveedor no soportado")
