preview_store = {}


def save_preview(resultado):
    preview_store[resultado.process_id] = resultado.factura


def get_preview(process_id):
    return preview_store.get(process_id)
