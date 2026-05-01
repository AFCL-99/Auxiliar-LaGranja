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
        </style>
    </head>
    <body>

        <h1>📊 Panel de Facturación</h1>

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
            <h3>📄 Actualizar factura</h3>
            <p>Procesar PDF y previsualizar</p>
            <a href="/compra/actualizar">Ir</a>
        </div>
        
        <div class="card">
            <h3>📄 Alza de precios</h3>
            <p>Consultar historico de precios</p>
            <form action="/analisis/factura" method="get">
                <input type="text" name="numero" placeholder="Ej: 7230"/>
                <button type="submit">Buscar</button>
            </form>
        </div>

    </body>
    </html>
    """