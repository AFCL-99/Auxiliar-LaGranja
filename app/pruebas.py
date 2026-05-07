response_ok = {
    "ok": True,
    "status":200,
    "mensaje": "Factura creada correctamente en SIIGO.",
    "siigo": {
        "id": "f4f2b8b7-7f34-4f92-aef5-5c9c12e6d111",
        "number": "FC-93821",
        "date": "2026-05-08",
        "total": 1854200,
        "supplier": {
            "name": "ITALCOL DE OCCIDENTE SA",
            "nit": "890901271"
        }
    }
}

response_error = {
    "ok": False,
    "mensaje": "El total de pagos no coincide con el total de la factura.",
    "detalle": {
        "Status": 400,
        "Errors": [
            {
                "Code": "invalid_total_payments",
                "Message": "The total payments value does not match invoice total.",
                "Params": [],
                "Detail": "Expected total: 1854200"
            }
        ]
    }
}

response_producto = {
    "ok": False,
    "mensaje": "Producto no válido en SIIGO.",
    "detalle": {
        "Status": 400,
        "Errors": [
            {
                "Code": "invalid_product",
                "Message": "El producto FER02 no existe.",
                "Detail": "Código inválido."
            }
        ]
    }
}

response_server = {
    "ok": False,
    "mensaje": "Error interno al crear la factura.",
    "detalle": "Timeout conectando con SIIGO API"
}