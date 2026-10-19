(async function () {
  const byId = (id) => document.getElementById(id);
  const alerts = byId("alertas");

  try {
    const r = await Api.get("/panel/resumen");
    byId("k-lotes").textContent = r.lotes ?? "—";
    byId("k-proceso").textContent = r.lotes_en_proceso ?? "—";
    byId("k-pedidos").textContent = r.pedidos_activos ?? "—";
    byId("k-kwh").textContent = r.kwh_30d ?? "—";

    alerts.replaceChildren();
    if (Array.isArray(r.alertas) && r.alertas.length) {
      r.alertas.forEach((a) => {
        const item = document.createElement("div");
        item.className = "alerta";
        const label = document.createElement("b");
        label.textContent = `${a.tipo ?? "Alerta"}: `;
        item.append(label, document.createTextNode(a.mensaje ?? ""));
        alerts.appendChild(item);
      });
    } else {
      const ok = document.createElement("div");
      ok.className = "ok";
      ok.textContent = "Sin alertas activas. Todo está funcionando con normalidad.";
      alerts.appendChild(ok);
    }
  } catch (e) {
    alerts.replaceChildren();
    const error = document.createElement("div");
    error.className = "alerta";
    error.textContent = e?.message || "No se pudo cargar el resumen. Intenta de nuevo.";
    alerts.appendChild(error);
  }
})();
