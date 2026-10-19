(function () {
  if (!Api.token()) { location.href = "login.html"; return; }

  const usuario = JSON.parse(localStorage.getItem("usuario") || "{}");
  const paginas = [
    ["panel.html", "Panel"],
    ["produccion.html", "Trazabilidad"],
    ["logistica.html", "Logística"],
    ["costos.html", "Energía y costos"],
    ["reportes.html", "Reportes"],
  ];
  const actual = location.pathname.split("/").pop();
  const nav = document.getElementById("nav");
  if (nav) {
    nav.className = "nav";
    nav.innerHTML =
      '<img src="img/logo.png" alt="NovaTech">' +
      paginas.map(([h, t]) => `<a href="${h}" class="${h === actual ? "activo" : ""}">${t}</a>`).join("") +
      `<span class="espacio"></span><span>${usuario.nombre || ""}</span>` +
      '<button class="btn sm sec" id="btn-salir">Salir</button>';
    document.getElementById("btn-salir").onclick = Api.salir;
  }
})();