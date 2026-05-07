from app.routes.index import generar_header
from app.utils.temp_store import temp_data

def formatear_moneda(valor):
    return f"${valor:,.2f}"


def generar_fila_item(item):
    encontrado = item.get("encontrado", False)

    clase = "ok" if encontrado else "error"

    return f"""
        <tr class="{clase}">
            <td>{item.get('codigo', '')}</td>
            <td>{item.get('nombre', '')}</td>
            <td>{item.get('cantidad', 0)}</td>
            <td>{formatear_moneda(item.get('precio', 0))}</td>
            <td>{formatear_moneda(item.get('descuento', 0))}</td>
            <td>{item.get('iva', 0)}%</td>
        </tr>
    """


def generar_totales_html(totales):
    return f"""
        <div class="totales">
            <p>Subtotal: <strong>{formatear_moneda(totales.get('subtotal', 0))}</strong></p>
            <p>Descuento: <strong>{formatear_moneda(totales.get('descuento', 0))}</strong></p>
            <p>IVA: <strong>{formatear_moneda(totales.get('iva', 0))}</strong></p>
            <p class="total">TOTAL: {formatear_moneda(totales.get('total', 0))}</p>
        </div>
    """


def generar_boton_crear_html(data, id_proceso):
    hay_productos_no_encontrados = data.get(
        "hay_productos_no_encontrados",
        False
    )

    if hay_productos_no_encontrados:
        return f"""
            <div class="advertencia">
                <strong>⚠️ Advertencia:</strong>
                Hay productos no encontrados en el maestro.
                Estos productos se subirán a SIIGO como
                <strong>PRODUCTO NUEVO</strong>.
            </div>

            <div class="acciones">
                <a href="/" class="btn btn-secondary">⬅️ Volver</a>

                <form id="formCrearFactura">
                    <input type="hidden" name="id_proceso" value="{id_proceso}">
                    <input type="hidden" name="confirmar_productos_nuevos" value="true">
                    <button type="submit" class="btn btn-danger">
                        Subir de todas formas
                    </button>
                </form>
            </div>
        """

    return f"""
        <form id="formCrearFactura" method="post">
            <input type="hidden" name="id_proceso" value="{id_proceso}">
            <button type="submit" class="btn btn-success">
                ✅ Crear factura en SIIGO
            </button>
        </form>
    """


def generar_tabla_html(data, id_proceso):
    items = data.get("items", [])
    factura_id = data.get("factura_id", "")
    proveedor = data.get("proveedor", "")
    totales = data.get("totales", {})

    filas = "".join(
        generar_fila_item(item)
        for item in items
    )

    html_totales = generar_totales_html(totales)
    header = generar_header()
    boton_crear = generar_boton_crear_html(
        data,
        id_proceso
    )

    return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f8f9fa;
                    color: #212529;
                }}
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 999;
                    inset: 0;
                    background: rgba(0, 0, 0, 0.45);
                    align-items: center;
                    justify-content: center;
                }}

                .modal-content {{
                    background: white;
                    width: 460px;
                    max-width: 90%;
                    padding: 28px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
                }}

                .loader {{
                    margin: 0 auto 20px auto;
                    width: 46px;
                    height: 46px;
                    border: 5px solid #e9ecef;
                    border-top: 5px solid #198754;
                    border-radius: 50%;
                    animation: spin 0.9s linear infinite;
                }}

                @keyframes spin {{
                    to {{
                        transform: rotate(360deg);
                    }}
                }}

                .modal-acciones {{
                    display: flex;
                    justify-content: center;
                    gap: 12px;
                    margin-top: 22px;
                    flex-wrap: wrap;
                }}

                #modalDetalle {{
                    text-align: left;
                    background: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    max-height: 220px;
                    overflow: auto;
                    font-size: 13px;
                }}

                .container {{
                    background: white;
                    padding: 24px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                }}

                h2 {{
                    margin-bottom: 5px;
                }}

                .proveedor {{
                    color: #555;
                    margin-bottom: 20px;
                }}

                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 20px;
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

                .totales {{
                    margin-top: 20px;
                    padding: 15px;
                    background: #f1f3f5;
                    border-radius: 8px;
                    width: 320px;
                }}

                .totales p {{
                    margin: 6px 0;
                }}

                .total {{
                    font-size: 18px;
                    font-weight: bold;
                }}

                .advertencia {{
                    margin-top: 20px;
                    padding: 15px;
                    background: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeeba;
                    border-radius: 8px;
                }}

                .acciones {{
                    display: flex;
                    gap: 10px;
                    align-items: center;
                    margin-top: 20px;
                }}

                .btn {{
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    text-decoration: none;
                    display: inline-block;
                }}

                .btn-success {{
                    background-color: green;
                }}

                .btn-danger {{
                    background-color: #dc3545;
                }}

                .btn-secondary {{
                    background-color: #6c757d;
                }}
            </style>
        </head>
        <script>
            document.addEventListener("DOMContentLoaded", function () {{

                const form = document.getElementById("formCrearFactura");

                if (!form) {{
                    console.error("No se encontró formCrearFactura");
                    return;
                }}

                form.addEventListener("submit", async function(e) {{
                    e.preventDefault();

                    const formData = new FormData(form);

                    const modal = document.getElementById("modalCarga");
                    const loader = document.getElementById("loader");
                    const titulo = document.getElementById("modalTitulo");
                    const mensaje = document.getElementById("modalMensaje");
                    const detalle = document.getElementById("modalDetalle");
                    const acciones = document.getElementById("modalAcciones");

                    modal.style.display = "flex";
                    loader.style.display = "block";

                    titulo.textContent = "Subiendo factura...";
                    mensaje.textContent = "Estamos enviando la factura a SIIGO.";

                    detalle.style.display = "none";
                    detalle.textContent = "";

                    acciones.innerHTML = "";

                    try {{

                        const response = await fetch("/compra/crear", {{
                            method: "POST",
                            body: formData
                        }});

                        const data = await response.json();

                        loader.style.display = "none";

                        if (data.ok === true || data.ok === "true") {{

                            titulo.textContent = "✅ Factura creada correctamente";
                            mensaje.textContent = data.mensaje;

                            acciones.innerHTML = `
                                <a href="/" class="btn btn-secondary">
                                    Volver al inicio
                                </a>

                                <form action="/analisis/factura" method="get">
                                    <input type="hidden" name="numero" value="${{obtenerNumeroFactura()}}">
                                    <button type="submit" class="btn btn-success">
                                        Ver análisis de precio
                                    </button>
                                </form>
                            `;

                        }} else {{

                            titulo.textContent = "❌ Error al crear factura";
                            mensaje.textContent = data.mensaje || "SIIGO rechazó la factura.";

                            detalle.style.display = "block";
                            detalle.textContent = JSON.stringify(data.detalle || data, null, 2);

                            acciones.innerHTML = `
                                <a href="/compra/preview?id_proceso=${{formData.get("id_proceso")}}"
                                class="btn btn-secondary">
                                    Volver a la preview
                                </a>
                            `;
                        }}

                    }} catch (error) {{

                        loader.style.display = "none";

                        titulo.textContent = "❌ Error de conexión";

                        mensaje.textContent =
                            "No se pudo conectar con el servidor.";

                        detalle.style.display = "block";

                        detalle.textContent = error.toString();

                        acciones.innerHTML = `
                            <a href="/compra/preview?id_proceso=${{formData.get("id_proceso")}}"
                            class="btn btn-secondary">
                                Volver a la preview
                            </a>
                        `;
                    }}
                }});

            }});

            function obtenerNumeroFactura() {{
                const titulo = document.querySelector("h2").textContent;
                const match = titulo.match(/(\d+)$/);
                return match ? match[1] : "";
            }}
            </script>
        <body>
            {header}
            <div class="container">
                <h2>Factura: {factura_id}</h2>
                <p class="proveedor">Proveedor: {proveedor}</p>

                <table>
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>Descuento</th>
                            <th>IVA</th>
                        </tr>
                    </thead>

                    <tbody>
                        {filas}
                    </tbody>
                </table>

                {html_totales}

                <br>

                {boton_crear}
            </div>

            <div id="modalCarga" class="modal">
                <div class="modal-content">
                    <div id="loader" class="loader"></div>

                    <h2 id="modalTitulo">Subiendo factura...</h2>

                    <p id="modalMensaje">
                        Estamos enviando la factura a SIIGO.
                    </p>

                    <pre id="modalDetalle" style="display:none;"></pre>

                    <div id="modalAcciones" class="modal-acciones"></div>
                </div>
            </div>
        </body>
        </html>
    """

def generar_tabla_cierre(data):
    header = generar_header()
    html = f"""
    <html>
    {header}
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #ccc; padding: 6px; }}
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