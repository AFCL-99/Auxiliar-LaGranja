from app.providers.alimentosPolar import AlimentosPolarProvider
from app.providers.contegral import contegralProvider
from app.providers.inversionesAgrocosur import InversionesAgrocosurProvider
from app.providers.sierraPineda import SierraPinedaProvider
from app.providers.tamayoPolanco import TamayoPolancoProvider

providers = [
    contegralProvider(),
    SierraPinedaProvider(),
    TamayoPolancoProvider(),
    InversionesAgrocosurProvider(),
    AlimentosPolarProvider(),
]


def detectar_provedor(texto: str):
    for provider in providers:
        if provider.detect(texto):
            return provider

    raise Exception("Proveedor no soportado")
