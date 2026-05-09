import pdfkit
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from num2words import num2words

env = Environment(
    loader=FileSystemLoader("app/templates")
)

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


def generar_pdf(tercero: dict,response: dict):

    template = env.get_template("reciboPago.html")
    
    fecha_formateada = datetime.strptime(
        response.get("date"),
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    banco = "BANCOLOMBIA"
    if(int(response["payment"]["id"])==4389):
        banco = "DAVIVIENDA"

    valor = float(response["payment"]["value"])

    formateado = f"{valor:,.1f}"

    datos = {
        "Nombre_tercero": tercero.get("Nombre"),
        "NIT_tercero": tercero.get("nit"),
        "Direccion_tercero": tercero.get("direccion"),
        "Telefono_tercero": tercero.get("telefono"),
        "Ciudad_tercero": tercero.get("ciudad"),
        "fecha_pago": response.get("date"),
        "numero_RP": response.get("number"),
        "valor":formateado,
        "concepto_fecha": fecha_formateada,
        "BANCO": banco,
        "observacion":response.get("observations"),
        "valor_en_letras": num2words(int(response["payment"]["value"]), lang='es')
    }
    html = template.render(**datos)
    ruta_pdf = f"RC-1-{response.get('number')}.pdf"
    pdfkit.from_string(
        html,
        ruta_pdf,
        configuration=config
    )
    return ruta_pdf
