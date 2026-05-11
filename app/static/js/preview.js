document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formCrearFactura");

    if (!form) {
        console.error("No se encontró formCrearFactura");
        return;
    }

    form.addEventListener("submit", async function(e) {
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

        try {

            const response = await fetch("/compra/crear", {
                method: "POST",
                body: formData
            });

            const text = await response.text();

            console.log(text);

            const data = JSON.parse(text);
            const numeroFactura = data?.siigo?.number || "";
            loader.style.display = "none";

            if (data.ok === true || data.ok === "true") {

                titulo.textContent = "✅ Factura creada correctamente";
                mensaje.textContent = data.mensaje;

                acciones.innerHTML = `
                    <a href="/" class="btn btn-secondary">
                        Volver al inicio
                    </a>
                    <form action="/analisis/factura" method="get">
                        <input type="hidden" name="numero" value="${numeroFactura}">
                        <button type="submit" class="btn btn-success">
                            Ver análisis de precio
                        </button>
                    </form>
                `;

            } else {

                titulo.textContent = "❌ Error al crear factura";
                mensaje.textContent = data.mensaje || "SIIGO rechazó la factura.";
            
                acciones.innerHTML = `
                    <a href="/compra/preview/${formData.get("process_id")}"
                    class="btn btn-secondary">
                        Volver a la preview
                    </a>
                `;
            }

        } catch (error) {

            loader.style.display = "none";

            titulo.textContent = "❌ Error de conexión";

            mensaje.textContent =
                "No se pudo conectar con el servidor.";

            detalle.style.display = "block";

            detalle.textContent = error.toString();

            acciones.innerHTML = `
                <a href="/compra/preview/${formData.get("process_id")}"
                class="btn btn-secondary">
                    Volver a la preview
                </a>
            `;
        }
    });

});

function obtenerNumeroFactura() {
    const titulo = document.querySelector("h2").textContent;
    const match = titulo.match(/(\d+)$/);
    return match ? match[1] : "";
}