(async function () {
  try {
    const r = await Api.get("/panel/resumen");
    document.getElementById("k-lotes").textContent = r.lotes;
    document.getElementById("k-proceso").textContent = r.lotes_en_proceso;
    document.getElementById("k-pedidos").textContent = r.pedidos_activos;
    document.getElementById("k-kwh").textContent = r.kwh_30d;
    const el = document.getElementById("alertas");
    el.innerHTML = r.alertas.length
      ? r.alertas.map((a) => `<div class="alerta"><b>${a.tipo}:</b> ${a.mensaje}</div>`).join("")
      : '<div class="ok">Sin alertas activas.</div>';
  } catch (e) {
    document.getElementById("alertas").textContent = e.message;
  }
})();