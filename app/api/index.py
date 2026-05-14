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
            .drop-zone {
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;

                height: 120px;
                padding: 20px;
                border: 2px dashed #198754;
                border-radius: 12px;
                background: #f8fff9;
                color: #198754;
                cursor: pointer;
                margin: 15px 0;
                font-weight: bold;
            }

            .drop-zone input {
                display: none;
            }

            .btn {
                height: 52px;
                padding: 0 24px;
                border: none;
                border-radius: 7px;
                cursor: pointer;
                font-size: 16px;
                color: white;
                text-decoration: none;

                display: inline-flex;
                align-items: center;
                justify-content: center;
            }

            .btn-success {
                background-color: green;
            }

            .btn-danger {
                background-color: #dc3545;
            }

            .btn-secondary {
                background-color: #6c757d;
            }

            .acciones {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-top: 20px;
            }

            .acciones form {
                margin: 0;
            }
        </style>
    </head>
    <body>

        <h1>📊 Auxiliar Siigo</h1>

        <div class="card">
            <h3>📄 Factura de compra</h3>
            <p>Procesar PDF y previsualizar</p>

            <form action="/compra/preview" method="post" enctype="multipart/form-data">
                <label class="drop-zone">
                    <input type="file" name="file" accept="application/pdf" required>
                    <span>Arrastra el PDF aquí o haz clic para seleccionarlo</span>
                </label>

                <button type="submit" class="btn btn-success">
                    Procesar factura
                </button>
            </form>
        </div>
        <div class="card">
            <h3>📄 Alza de precios</h3>
            <p>Consultar historico de precios</p>
            <form action="/compra/analizar" method="get">
                <input type="text" name="numero" placeholder="Ej: 7230"/>
                <button type="submit">Buscar</button>
            </form>
        </div>
        
        <div class="card">
            <h3>📄 Planillar</h3>
            <p>Consultar deudas por pagar</p>
            <form action="/compra/planillar" method="get">
                <input type="text" name="numero" placeholder="Ej: 7230"/>
                <button type="submit">Buscar</button>
            </form>
        </div>
        
        <div class="card">
            <h3>🧾 Facturar cotización</h3>
            <p>Crear factura desde cotización</p>

            <form action="/venta/crear" method="post">
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

    </body>
    </html>
    <script>
    document.querySelectorAll(".drop-zone input").forEach(input => {
        input.addEventListener("change", function () {
            const label = this.closest(".drop-zone");
            const span = label.querySelector("span");

            if (this.files.length > 0) {
                span.textContent = "📄 " + this.files[0].name;
            }
        });
    });
</script>
    """
