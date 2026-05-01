from app.utils.temp_store import temp_data
def generar_tabla_html(data, id_proceso):
    filas = ""
    items = data.get("items")
    factura_id = data.get("factura_id")
    totales = data.get("totales")

    html_totales = f"""
        <p>Subtotal: ${totales['subtotal']:,.2f}</p>
        <p>Descuento: ${totales['descuento']:,.2f}</p>
        <p>IVA: ${totales['iva']:,.2f}</p>
        <p><strong>TOTAL: ${totales['total']:,.2f}</strong></p>
        """
    for item in items:
        color = "#d4edda" if item["encontrado"] else "#f8d7da"
        filas += f"""
        <tr style="background-color:{color}">
            <td>{item['codigo']}</td>
            <td>{item['nombre']}</td>
            <td>{item['cantidad']}</td>
            <td>{item['precio']}</td>
            <td>{item['descuento']}</td>
            <td>{item['iva']}</td>
        </tr>
        """    
    return f"""
        <html>
        <head>
        <style>
            body {{
                font-family: Arial;
                margin: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .ok {{
                background-color: #d4edda;
            }}
            .error {{
                background-color: #f8d7da;
            }}
            .btn {{
                background-color: green;
                color: white;
                padding: 10px 20px;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }}
        </style>
        </head>
        <body>

        <h2>Factura: {factura_id}</h2>

        <table>
        <tr>
        <th>Código</th>
        <th>Producto</th>
        <th>Cantidad</th>
        <th>Precio</th>
        <th>Descuento</th>
        <th>Iva</th>
        </tr>

        {filas}

        </table>

        <br>
        {html_totales}
        <br>
        <form action="/compra/crear" method="post">
            <input type="hidden" name="id_proceso" value="{id_proceso}">
            <button class="btn">✅ Crear factura en Siigo</button>
        </form>

        </body>
        </html>
        """

def generar_tabla_cierre(data):
    html = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            td, th { border: 1px solid #ccc; padding: 6px; }
        </style>
    </head>
    <body>
    <table id="tabla">
    <tr>
        <th>Fecha</th>
        <th></th>
        <th>Cliente</th>
        <th>Comprobante</th>
        <th>Cartera</th>
        <th>Efectivo</th>
        <th>Crédito</th>
        <th>Banco</th>
        <th>Método</th>
    </tr>
    """

    for row in data:
        html += "<tr>"
        for col in row:
            html += f"<td>{col}</td>"
        html += "</tr>"

    html += """
    </table>
    <button onclick="copiar()">📋 Copiar</button>

    <script>

    function copiar() {
        let texto = "";
        const filas = document.querySelectorAll("#tabla tr:has(td)");
        
        filas.forEach(fila => {
            let cols = fila.querySelectorAll("td");
            let linea = [];

            cols.forEach(c => linea.push(c.innerText));

            texto += linea.join("\\t") + "\\n";
        });

        navigator.clipboard.writeText(texto);
    }
    </script>

    </body>
    </html>
    """

    return html