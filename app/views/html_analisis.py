def generar_html_analisis(data):

    filas = ""

    for item in data["items"]:

        color = {
            "▲": "#d4edda",
            "▼": "#f8d7da",
            "▬": "#fff3cd",
            "✚": "#d1ecf1"
        }[item["estado"]]

        fecha = item["fecha"].strftime("%Y-%m") if item["fecha"] else ""

        filas += f"""
        <tr style="background:{color}">
            <td>{item['codigo']}</td>
            <td>{item['descripcion']}</td>
            <td>${item['precio_anterior']:,.2f}</td>
            <td>${item['precio_actual']:,.2f}</td>
            <td>{item.get('comprobante','')}</td>
            <td>{fecha}</td>
            <td>${item['diferencia']:,.2f}</td>
            <td>{item['porcentaje']:.2%}</td>
            <td>{item['estado']}</td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family: Arial; padding:20px;">

        <h2>📊 Análisis de precios</h2>

        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>Código</th>
                <th>Producto</th>
                <th>Precio Anterior</th>
                <th>Precio Actual</th>
                <th>Comp</th>
                <th>Fecha</th>
                <th>Δ Precio</th>
                <th>% Var</th>
                <th>Estado</th>
            </tr>
            {filas}
        </table>
    </body>
    </html>
    """