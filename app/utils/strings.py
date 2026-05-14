import re


def normalizar_espacios(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()
