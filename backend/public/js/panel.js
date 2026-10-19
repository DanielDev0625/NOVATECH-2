(async function () {
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => Number(n ?? 0).toLocaleString("es-CO", { maximumFractionDigits: 1 });
  const dinero = (n) => "$ " + Number(n ?? 0).toLocaleString("es-CO", { maximumFractionDigits: 0 });

  document.querySelectorAll("[data-ico]").forEach((el) => { el.innerHTML = Ico[el.dataset.ico] || ""; });

  // · Variación porcentual con flecha; "invertido" cuando bajar es bueno (por ejemplo, los costos).
  function delta(v, texto, invertido = false) {
    if (v === null || v === undefined) return `<span class="delta neutro">Sin datos previos</span> <span>${texto}</span>`;
    const bueno = invertido ? v <= 0 : v >= 0;
    const flecha = v >= 0 ? Ico.subir : Ico.bajar;
    const signo = v > 0 ? "+" : "";
    return `<span class="delta ${bueno ? "sube" : "mal"}">${flecha}${signo}${num(v)}%</span> <span>${texto}</span>`;
  }

  function hace(iso) {
    const min = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
    if (min < 1) return "Ahora";
    if (min < 60) return `Hace ${min} min`;
    if (min < 1440) return `Hace ${Math.round(min / 60)} h`;
    return `Hace ${Math.round(min / 1440)} d`;
  }

  // · Máximo "redondo" para el eje del gráfico (1, 2, 5 x 10^n).
  function maximoBonito(m) {
    if (m <= 0) return 4;
    const e = Math.pow(10, Math.floor(Math.log10(m)));
    const f = m / e;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * e;
  }

  const ICONO_ACT = { pedido: ["c-verde", Ico.camion], lote: ["c-azul", Ico.grafica], energia: ["c-naranja", Ico.rayo] };

  let r;
  try {
    r = await resumenPanel();
  } catch (e) {
    const msg = `<div class="alerta">${esc(e?.message || "No se pudo cargar el resumen. Intenta de nuevo.")}</div>`;
    $("alertas").innerHTML = msg;
    $("actividad").innerHTML = '<p class="vacio">Sin datos disponibles.</p>';
    $("grafico").innerHTML = '<p class="vacio">Sin datos disponibles.</p>';
    return;
  }

  $("k-prod").textContent = num(r.produccion_hoy);
  $("f-prod").innerHTML = delta(r.produccion_variacion, "vs. ayer");
  $("k-transito").textContent = r.ordenes_transito ?? "—";
  $("s-transito").textContent = `de ${r.ordenes_activas ?? 0} activas`;
  $("f-transito").innerHTML = delta(r.ordenes_variacion, "pedidos vs. semana anterior");
  $("k-costo").textContent = dinero(r.costo_operacion);
  $("f-costo").innerHTML = delta(r.costo_variacion, "vs. 30 días anteriores", true);
  $("k-proceso").textContent = r.lotes_en_proceso ?? "—";
  $("s-proceso").textContent = `de ${r.lotes ?? 0} lotes`;
  $("f-proceso").innerHTML = `<span>${num(r.kwh_30d)} kWh consumidos en 30 días</span>`;

  // · Actividad reciente.
  const act = r.actividad || [];
  $("actividad").innerHTML = act.length
    ? act.map((a) => {
        const [color, ico] = ICONO_ACT[a.tipo] || ["c-azul", Ico.grafica];
        return `<div class="act-item"><span class="ico-cuadro ${color}">${ico}</span>
          <div><strong>${esc(a.titulo)}</strong><small>${esc(a.detalle)}</small></div><time>${hace(a.fecha)}</time></div>`;
      }).join("")
    : '<p class="vacio">Aún no hay movimientos. Registra un lote, un pedido o un consumo para verlos aquí.</p>';

  // · Gráfico de barras de los últimos 7 días.
  const semana = r.semana || [];
  const max = maximoBonito(Math.max(0, ...semana.map((d) => d.valor)));
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => `<span>${num(max * t)}</span>`).join("");
  $("grafico").innerHTML = `<div class="grafico"><div class="eje">${ticks}</div>${semana.map((d, i) => `
    <div class="barra-col" title="${esc(d.dia)}: ${num(d.valor)} unidades">
      <div class="barra ${i === semana.length - 1 ? "hoy" : ""}" style="height:calc((100% - 24px) * ${d.valor / max})"></div>
      <span>${esc(d.dia)}</span></div>`).join("")}</div>`;

  // · Alertas.
  const alertas = r.alertas || [];
  $("alertas").innerHTML = alertas.length
    ? alertas.slice(0, 3).map((a) => `<div class="alerta"><b>${esc(a.tipo ?? "Alerta")}:&nbsp;</b>${esc(a.mensaje ?? "")}</div>`).join("") +
      (alertas.length > 3 ? `<p style="margin-top:10px"><a class="enlace" href="reportes.html">Ver las ${alertas.length} alertas</a></p>` : "")
    : '<div class="ok">Sin alertas activas. Todo está funcionando con normalidad.</div>';
})();
