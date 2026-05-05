from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Panel</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                padding: 40px;
                background: #f5f5f5;
            }

            h1 {
                margin-bottom: 40px;
            }

            .card {
                display: inline-block;
                background: white;
                padding: 20px;
                margin: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                width: 250px;
            }

            a {
                text-decoration: none;
                color: white;
                background: #2e7d32;
                padding: 10px 15px;
                border-radius: 5px;
                display: inline-block;
                margin-top: 10px;
            }

            a:hover {
                background: #1b5e20;
            }
            button {
                margin-top: 10px;
                background-color: #2e7d32; /* mismo verde */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                cursor: pointer;
            }

            button:hover {
                background: #1b5e20;
            }
        </style>
    </head>
    <body>

        <h1>📊 Auxiliar Siigo</h1>

        <div class="card">
            <h3>📄 Factura de compra</h3>
            <p>Procesar PDF y previsualizar</p>
            <a href="/compra/preview">Ir</a>
        </div>
        <div class="card">
            <h3>📄 Cierre</h3>
            <p>Generar cierre diario</p>
            <a href="/cierre">Ir</a>
        </div>
        
        <div class="card">
            <h3>📄 Alza de precios</h3>
            <p>Consultar historico de precios</p>
            <form action="/analisis/factura" method="get">
                <input type="text" name="numero" placeholder="Ej: 7230"/>
                <button type="submit">Buscar</button>
            </form>
        </div>

        <div class="card">
            <h3>🧾 Facturar cotización</h3>
            <p>Crear factura desde cotización</p>

            <form action="/cotizacion/facturar" method="post">
                <input type="text" name="numero" placeholder="Ej: 1562" required/>

                <label>Vencimiento:</label>
                <select name="tipo_vencimiento">
                    <option value="hoy">Hoy</option>
                    <option value="15">15 días</option>
                    <option value="fin_mes">Fin de mes</option>
                </select>

                <button type="submit">Facturar</button>
            </form>
        </div>

        <div class="card">
            <h3>🧾 Cambiar bodega</h3>
            <p>Trasladar facturas entre bodegas</p>

            <form action="/compra/trasladar" method="post">
                <input type="number" name="id_factura" placeholder="Ej: 1562" required/>

                <label>Nueva bodega:</label>
                <select name="nueva_bodega">
                    <option value=69>Principal</option>
                    <option value=887>Medicamentos</option>
                    <option value=73>Plantas Neiva</option>
                </select>

                <button type="submit">Trasladar</button>
                <p id="status"></p>
            </form>
        </div>

    </body>
    </html>
    """

def generar_header():
    return """
    <header style="margin-bottom:20px;">
        <a href="/" style="text-decoration:none; font-weight:bold;">
            ⬅ Volver al inicio
        </a>
        <hr>
    </header>
    """