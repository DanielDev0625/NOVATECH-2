const $ = (s, r = document) => r.querySelector(s);
const fmt = (n, d = 2) => Number(n ?? 0).toLocaleString("es-CO", { maximumFractionDigits: d });
const money = (n) => "$ " + Number(n ?? 0).toLocaleString("es-CO", { maximumFractionDigits: 0 });
const fecha = (s) => (s ? new Date(s + (s.endsWith("Z") ? "" : "Z")).toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" }) : "—");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function toast(msg, error = false) {
  const t = document.createElement("div");
  t.className = "toast" + (error ? " error" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

function datosForm(form) {
  const d = {};
  new FormData(form).forEach((v, k) => (d[k] = v));
  form.querySelectorAll("[data-num]").forEach((i) => {
    if (d[i.name] === "" || d[i.name] === undefined) delete d[i.name];
    else d[i.name] = Number(d[i.name]);
  });
  Object.keys(d).forEach((k) => { if (d[k] === "") delete d[k]; });
  return d;
}

function tabla(el, cols, rows) {
  if (!rows.length) { el.innerHTML = '<p class="vacio">Sin registros todavía.</p>'; return; }
  el.innerHTML =
    '<div class="scroll"><table><thead><tr>' + cols.map((c) => `<th>${c.t}</th>`).join("") +
    "</tr></thead><tbody>" +
    rows.map((r) => "<tr>" + cols.map((c) => `<td>${c.f(r)}</td>`).join("") + "</tr>").join("") +
    "</tbody></table></div>";
}

function llenarSelect(sel, items, valor, texto, vacio) {
  sel.innerHTML = (vacio ? `<option value="">${vacio}</option>` : "") +
    items.map((i) => `<option value="${esc(valor(i))}">${esc(texto(i))}</option>`).join("");
}

async function seguro(fn) {
  try { await fn(); } catch (e) { toast(e.message, true); }
}

const Secciones = {};

/* ---------------- Trazabilidad ---------------- */
Secciones.produccion = async () => {
  const cargar = async () => {
    const lotes = await Api.get("/lotes");
    tabla($("#tabla-lotes"), [
      { t: "Código", f: (r) => `<b>${esc(r.codigo)}</b>` },
      { t: "Producto", f: (r) => esc(r.producto) },
      { t: "Cantidad", f: (r) => `${fmt(r.cantidad)} ${esc(r.unidad)}` },
      { t: "Estado", f: (r) => `<span class="tag">${esc(r.estado)}</span>` },
      { t: "Creado", f: (r) => fecha(r.creado_en) },
      { t: "", f: (r) => `<button class="btn sm" data-ver="${esc(r.codigo)}">Etapas</button>` },
    ], lotes);
  };

  const verLote = async (codigo) => {
    const l = await Api.get("/lotes/" + encodeURIComponent(codigo));
    $("#detalle").innerHTML = `
      <h3>Lote ${esc(l.codigo)} — ${esc(l.producto)}</h3>
      ${l.etapas.map((e) => `
        <div class="etapa" data-etapa="${e.id}">
          <strong style="min-width:110px">${esc(e.nombre)}</strong>
          <small>límite ${fecha(e.fecha_limite)}</small>
          <input data-campo="responsable" placeholder="Responsable" value="${esc(e.responsable)}">
          <input data-campo="observaciones" placeholder="Observaciones" value="${esc(e.observaciones)}">
          <label style="flex-direction:row"><input type="checkbox" data-campo="control_calidad" ${e.control_calidad ? "checked" : ""}> Calidad OK</label>
          <label style="flex-direction:row"><input type="checkbox" data-campo="completada" ${e.completada ? "checked" : ""}> Completada</label>
          <button class="btn sm" data-guardar="${e.id}" data-codigo="${esc(l.codigo)}">Guardar</button>
        </div>`).join("")}
      <p><button class="btn" data-pdf="${esc(l.codigo)}">Certificado PDF con QR</button>
      <a class="btn sec" target="_blank" href="modulo.html?codigo=${encodeURIComponent(l.codigo)}">Vista pública</a></p>`;
  };

  $("#form-lote").addEventListener("submit", (e) => {
    e.preventDefault();
    seguro(async () => {
      const l = await Api.post("/lotes", datosForm(e.target));
      e.target.reset();
      toast("Lote creado: " + l.codigo);
      await cargar();
      await verLote(l.codigo);
    });
  });

  $("#btn-actualizar").addEventListener("click", () => seguro(async () => { await cargar(); toast("Lista actualizada"); }));

  $("#tabla-lotes").addEventListener("click", (e) => {
    const b = e.target.closest("[data-ver]");
    if (b) seguro(() => verLote(b.dataset.ver));
  });

  $("#detalle").addEventListener("click", (e) => {
    const g = e.target.closest("[data-guardar]");
    const p = e.target.closest("[data-pdf]");
    if (g) seguro(async () => {
      const fila = g.closest(".etapa");
      const v = (c) => fila.querySelector(`[data-campo=${c}]`);
      await Api.patch("/etapas/" + g.dataset.guardar, {
        responsable: v("responsable").value, observaciones: v("observaciones").value,
        control_calidad: v("control_calidad").checked, completada: v("completada").checked,
      });
      toast("Etapa actualizada");
      await cargar();
      await verLote(g.dataset.codigo);
    });
    if (p) seguro(() => Api.descargar(`/publico/lotes/${encodeURIComponent(p.dataset.pdf)}/certificado`));
  });

  await cargar();
};

/* ---------------- Logística ---------------- */
Secciones.logistica = async () => {
  const ciudades = await Api.get("/logistica/ciudades");
  ["#ped-origen", "#ped-destino", "#ruta-origen"].forEach((s) => llenarSelect($(s), ciudades, (c) => c, (c) => c));
  $("#ruta-destinos").innerHTML = ciudades.map((c) => `<option>${esc(c)}</option>`).join("");
  let transportistas = [], vehiculos = [];

  const cargar = async () => {
    [transportistas, vehiculos] = await Promise.all([Api.get("/logistica/transportistas"), Api.get("/logistica/vehiculos")]);
    const pedidos = await Api.get("/logistica/pedidos");
    // · Indicadores de la parte superior.
    $("#kpi-transportistas").textContent = transportistas.length;
    $("#kpi-vehiculos").textContent = vehiculos.length;
    $("#kpi-pedidos").textContent = pedidos.filter((p) => ["Pendiente", "En ruta"].includes(p.estado)).length;
    $("#kpi-entregas").textContent = pedidos.filter((p) => p.estado === "Entregado").length;
    llenarSelect($("#veh-transportista"), transportistas, (t) => t.id, (t) => t.nombre);
    llenarSelect($("#ped-transportista"), transportistas, (t) => t.id, (t) => t.nombre, "— sin asignar —");
    llenarSelect($("#ped-vehiculo"), vehiculos, (v) => v.id, (v) => `${v.placa} (${v.transportista})`, "— sin asignar —");

    tabla($("#tabla-transportistas"), [
      { t: "Nombre", f: (r) => esc(r.nombre) }, { t: "Teléfono", f: (r) => esc(r.telefono) },
      { t: "Valoración", f: (r) => "★ " + fmt(r.valoracion, 1) },
      { t: "Costo/km", f: (r) => money(r.costo_km) }, { t: "Vehículos", f: (r) => r.vehiculos },
    ], transportistas);
    tabla($("#tabla-vehiculos"), [
      { t: "Placa", f: (r) => `<b>${esc(r.placa)}</b>` }, { t: "Tipo", f: (r) => esc(r.tipo) },
      { t: "Modelo", f: (r) => esc(r.modelo) }, { t: "Capacidad", f: (r) => fmt(r.capacidad_kg, 0) + " kg" },
      { t: "Transportista", f: (r) => esc(r.transportista) },
    ], vehiculos);
    tabla($("#tabla-pedidos"), [
      { t: "#", f: (r) => r.id }, { t: "Cliente", f: (r) => esc(r.cliente) },
      { t: "Ruta", f: (r) => `${esc(r.origen)} → ${esc(r.destino)} (${fmt(r.distancia_km, 0)} km)` },
      { t: "Transporte", f: (r) => esc(r.transportista) + (r.placa ? ` · ${esc(r.placa)}` : "") },
      { t: "Tarifa", f: (r) => money(r.tarifa) }, { t: "Comisión", f: (r) => money(r.comision) },
      { t: "Estado", f: (r) => `<select data-estado="${r.id}">${["Pendiente", "En ruta", "Entregado", "Cancelado"]
          .map((s) => `<option ${s === r.estado ? "selected" : ""}>${s}</option>`).join("")}</select>` },
    ], pedidos);
  };

  const enviar = (sel, ruta, ok) => $(sel).addEventListener("submit", (e) => {
    e.preventDefault();
    seguro(async () => { await Api.post(ruta, datosForm(e.target)); e.target.reset(); toast(ok); await cargar(); });
  });
  enviar("#form-transportista", "/logistica/transportistas", "Transportista registrado");
  enviar("#form-vehiculo", "/logistica/vehiculos", "Vehículo registrado");
  enviar("#form-pedido", "/logistica/pedidos", "Pedido creado");

  $("#tabla-pedidos").addEventListener("change", (e) => {
    const s = e.target.closest("[data-estado]");
    if (s) seguro(async () => { await Api.patch(`/logistica/pedidos/${s.dataset.estado}/estado`, { estado: s.value }); toast("Estado actualizado"); });
  });

  $("#btn-sugerir").addEventListener("click", () => seguro(async () => {
    const o = $("#ped-origen").value, d = $("#ped-destino").value, p = $("#form-pedido [name=peso_kg]").value || 0;
    const r = await Api.get(`/logistica/sugerencias?origen=${encodeURIComponent(o)}&destino=${encodeURIComponent(d)}&peso_kg=${p}`);
    $("#sugerencias").innerHTML = `<p>Distancia estimada: <b>${fmt(r.distancia_km, 0)} km</b></p>` +
      (r.opciones.length ? r.opciones.map((x, i) => `<div class="${i === 0 ? "ok" : "alerta"}" style="border-left-color:${i === 0 ? "" : "#94a3b8"};background:${i === 0 ? "" : "#f8fafc"}">
        ${i === 0 ? "⭐ Mejor opción: " : ""}<b>${esc(x.transportista)}</b> · ${esc(x.placa)} · ${fmt(x.capacidad_kg, 0)} kg · ★ ${fmt(x.valoracion, 1)} · ${money(x.costo)}</div>`).join("")
        : '<p class="vacio">No hay transportistas con vehículo disponible para ese peso.</p>');
  }));

  $("#form-ruta").addEventListener("submit", (e) => {
    e.preventDefault();
    seguro(async () => {
      const destinos = [...$("#ruta-destinos").selectedOptions].map((o) => o.value);
      if (!destinos.length) throw new Error("Selecciona al menos un destino");
      const r = await Api.post("/logistica/ruta", { origen: $("#ruta-origen").value, destinos });
      $("#ruta-resultado").innerHTML = r.tramos.map((t, i) => `<div>${i + 1}. ${esc(t.desde)} → <b>${esc(t.hasta)}</b> (${fmt(t.km, 0)} km)</div>`).join("") +
        `<p><b>Total: ${fmt(r.total_km, 0)} km</b></p>`;
    });
  });

  await cargar();
};

/* ---------------- Energía y costos ---------------- */
Secciones.costos = async () => {
  const cargar = async () => {
    const [consumos, tarifas, res, rec] = await Promise.all([
      Api.get("/energia/consumos"), Api.get("/energia/tarifas"),
      Api.get("/energia/resumen"), Api.get("/energia/recomendacion"),
    ]);
    $("#recomendacion").textContent = rec.mensaje;
    tabla($("#tabla-consumos"), [
      { t: "Fecha", f: (r) => fecha(r.fecha) }, { t: "Máquina", f: (r) => esc(r.maquina) },
      { t: "Proceso", f: (r) => esc(r.proceso) }, { t: "Lote", f: (r) => esc(r.lote) || "—" },
      { t: "kWh", f: (r) => fmt(r.kwh) }, { t: "Tarifa", f: (r) => money(r.tarifa_kwh) },
      { t: "Costo", f: (r) => money(r.costo) },
    ], consumos);
    tabla($("#tabla-tarifas"), [
      { t: "Franja", f: (r) => esc(r.nombre) }, { t: "Horario", f: (r) => `${r.hora_inicio}:00 – ${r.hora_fin}:00` },
      { t: "Valor kWh", f: (r) => money(r.valor_kwh) },
    ], tarifas);
    tabla($("#tabla-procesos"), [
      { t: "Proceso", f: (r) => esc(r.proceso) }, { t: "kWh (30 días)", f: (r) => fmt(r.kwh_actual) },
      { t: "kWh (30 días previos)", f: (r) => fmt(r.kwh_previo) },
      { t: "Variación", f: (r) => r.kwh_previo ? fmt(((r.kwh_actual - r.kwh_previo) / r.kwh_previo) * 100, 0) + " %" : "—" },
    ], res.por_proceso);
    tabla($("#tabla-costo-lote"), [
      { t: "Lote", f: (r) => esc(r.lote) }, { t: "kWh", f: (r) => fmt(r.kwh) }, { t: "Costo estimado", f: (r) => money(r.costo) },
    ], res.por_lote);
  };

  const enviar = (sel, ruta, ok) => $(sel).addEventListener("submit", (e) => {
    e.preventDefault();
    seguro(async () => { await Api.post(ruta, datosForm(e.target)); e.target.reset(); toast(ok); await cargar(); });
  });
  enviar("#form-consumo", "/energia/consumos", "Consumo registrado");
  enviar("#form-tarifa", "/energia/tarifas", "Tarifa guardada");

  await cargar();
};

/* ---------------- Reportes ---------------- */
Secciones.reportes = async () => {
  const [alertas, h, res] = await Promise.all([
    Api.get("/reportes/alertas"), Api.get("/reportes/huella"), Api.get("/energia/resumen"),
  ]);
  $("#lista-alertas").innerHTML = alertas.length
    ? alertas.map((a) => `<div class="alerta"><b>${esc(a.tipo)}:</b> ${esc(a.mensaje)}</div>`).join("")
    : '<div class="ok">Sin alertas activas.</div>';
  $("#h-energia").textContent = fmt(h.co2_energia_kg, 1);
  $("#h-transporte").textContent = fmt(h.co2_transporte_kg, 1);
  $("#h-total").textContent = fmt(h.co2_total_kg, 1);
  $("#h-nota").textContent = `${fmt(h.kwh_total, 1)} kWh y ${fmt(h.km_total, 0)} km registrados. ${h.nota}`;
  tabla($("#tabla-procesos"), [
    { t: "Proceso", f: (r) => esc(r.proceso) }, { t: "kWh total", f: (r) => fmt(r.kwh) },
    { t: "Costo", f: (r) => money(r.costo) }, { t: "kWh 30 días", f: (r) => fmt(r.kwh_actual) },
    { t: "kWh 30 días previos", f: (r) => fmt(r.kwh_previo) },
  ], res.por_proceso);
};

/* ---------------- Consulta pública de lote (QR) ---------------- */
Secciones.modulo = async () => {
  const codigo = new URLSearchParams(location.search).get("codigo");
  const el = $("#resultado");
  const buscar = (c) => seguro(async () => {
    try {
      const l = await Api.get("/publico/lotes/" + encodeURIComponent(c));
      el.innerHTML = `<div class="tarjeta"><h2>${esc(l.codigo)}</h2>
        <p><b>${esc(l.producto)}</b> · ${fmt(l.cantidad)} ${esc(l.unidad)} · <span class="tag">${esc(l.estado)}</span></p>
        ${l.etapas.map((e) => `<div class="etapa"><strong style="min-width:120px">${esc(e.nombre)}</strong>
          <span>${e.completada ? "✅ " + fecha(e.fecha_real) : "⏳ pendiente (límite " + fecha(e.fecha_limite) + ")"}</span>
          <span>${e.control_calidad ? "Calidad OK" : "Sin control de calidad"}</span>
          <span>Resp.: ${esc(e.responsable) || "—"}</span></div>`).join("")}
        <p><button class="btn" id="btn-cert">Certificado PDF</button></p></div>`;
      $("#btn-cert").onclick = () => seguro(() => Api.descargar(`/publico/lotes/${encodeURIComponent(c)}/certificado`));
    } catch (e) {
      el.innerHTML = `<div class="alerta">${esc(e.message)}</div>`;
    }
  });
  $("#form-buscar").addEventListener("submit", (e) => { e.preventDefault(); buscar($("#codigo").value.trim()); });
  if (codigo) { $("#codigo").value = codigo; buscar(codigo); }
};

document.addEventListener("DOMContentLoaded", () => {
  const s = document.body.dataset.seccion;
  if (Secciones[s]) seguro(Secciones[s]);
});