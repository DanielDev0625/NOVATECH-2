const token = localStorage.getItem("token");

/* =========================
   PETICIONES
========================= */

async function apiGet(url) {

    const response = await fetch(url, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error("Error en GET");
    }

    return await response.json();
}

async function apiPost(url, data) {

    const response = await fetch(url, {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },

        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error("Error en POST");
    }

    return await response.json();
}

/* =========================
   KPI
========================= */

async function cargarKPIs() {

    const transportistas =
        await apiGet("/api/logistica/transportistas");

    const vehiculos =
        await apiGet("/api/logistica/vehiculos");

    const pedidos =
        await apiGet("/api/logistica/pedidos");

    document.getElementById("kpi-transportistas")
        .textContent = transportistas.length;

    document.getElementById("kpi-vehiculos")
        .textContent = vehiculos.length;

    document.getElementById("kpi-pedidos")
        .textContent = pedidos.length;

    document.getElementById("kpi-entregas")
        .textContent =
            pedidos.filter(
                p => p.estado === "Entregado"
            ).length;
}

/* =========================
   TRANSPORTISTAS
========================= */

async function cargarTransportistas() {

    const datos =
        await apiGet(
            "/api/logistica/transportistas"
        );

    const tabla =
        document.getElementById(
            "tabla-transportistas"
        );

    if (!datos.length) {

        tabla.innerHTML = `
            <p class="vacio">
                No hay transportistas registrados.
            </p>
        `;

        return;
    }

    tabla.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Teléfono</th>
                    <th>Valoración</th>
                    <th>Costo/km</th>
                    <th>Vehículos</th>
                </tr>
            </thead>

            <tbody>

                ${datos.map(t => `
                    <tr>
                        <td>${t.nombre}</td>
                        <td>${t.telefono}</td>
                        <td>${t.valoracion}</td>
                        <td>$${t.costo_km}</td>
                        <td>${t.vehiculos}</td>
                    </tr>
                `).join("")}

            </tbody>
        </table>
    `;

    const selectVehiculo =
        document.querySelector(
            'select[name="transportista_id"]'
        );

    const selectPedido =
        document.querySelector(
            'select[name="transportista"]'
        );

    selectVehiculo.innerHTML =
        '<option value="">Seleccionar</option>';

    selectPedido.innerHTML =
        '<option value="">Sin asignar</option>';

    datos.forEach(t => {

        selectVehiculo.innerHTML += `
            <option value="${t.id}">
                ${t.nombre}
            </option>
        `;

        selectPedido.innerHTML += `
            <option value="${t.id}">
                ${t.nombre}
            </option>
        `;
    });
}

/* =========================
   VEHICULOS
========================= */

async function cargarVehiculos() {

    const datos =
        await apiGet(
            "/api/logistica/vehiculos"
        );

    const tabla =
        document.getElementById(
            "tabla-vehiculos"
        );

    if (!datos.length) {

        tabla.innerHTML = `
            <p class="vacio">
                No hay vehículos registrados.
            </p>
        `;

        return;
    }

    tabla.innerHTML = `
        <table>

            <thead>
                <tr>
                    <th>Placa</th>
                    <th>Tipo</th>
                    <th>Modelo</th>
                    <th>Capacidad</th>
                    <th>Transportista</th>
                </tr>
            </thead>

            <tbody>

                ${datos.map(v => `
                    <tr>
                        <td>${v.placa}</td>
                        <td>${v.tipo}</td>
                        <td>${v.modelo}</td>
                        <td>${v.capacidad_kg}</td>
                        <td>${v.transportista}</td>
                    </tr>
                `).join("")}

            </tbody>

        </table>
    `;
}

/* =========================
   PEDIDOS
========================= */

async function cargarPedidos() {

    const datos =
        await apiGet(
            "/api/logistica/pedidos"
        );

    const tabla =
        document.getElementById(
            "tabla-pedidos"
        );

    if (!datos.length) {

        tabla.innerHTML = `
            <p class="vacio">
                No hay pedidos registrados.
            </p>
        `;

        return;
    }

    tabla.innerHTML = `
        <table>

            <thead>
                <tr>
                    <th>Cliente</th>
                    <th>Origen</th>
                    <th>Destino</th>
                    <th>Transportista</th>
                    <th>Vehículo</th>
                    <th>Estado</th>
                </tr>
            </thead>

            <tbody>

                ${datos.map(p => `
                    <tr>
                        <td>${p.cliente}</td>
                        <td>${p.origen}</td>
                        <td>${p.destino}</td>
                        <td>${p.transportista}</td>
                        <td>${p.placa}</td>
                        <td>${p.estado}</td>
                    </tr>
                `).join("")}

            </tbody>

        </table>
    `;
}

/* =========================
   FORMULARIOS
========================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await cargarTransportistas();
            await cargarVehiculos();
            await cargarPedidos();
            await cargarKPIs();

        } catch(error) {

            console.error(error);

        }

    }
);