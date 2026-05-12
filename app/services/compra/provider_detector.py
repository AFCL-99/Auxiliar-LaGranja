from app.providers.contegral import contegralProvider
from app.providers.sierraPineda import SierraPinedaProvider
from app.providers.tamayoPolanco import TamayoPolancoProvider

providers = [contegralProvider(), SierraPinedaProvider(), TamayoPolancoProvider()]


def detectar_provedor(texto: str):
    for provider in providers:
        if provider.detect(texto):
            return provider

    raise Exception("Proveedor no soportado")
