// Arma el marco común de las pantallas internas (menú lateral + barra superior) y exige sesión.
(function () {
  if (!Api.token()) { location.href = "login.html"; return; }

  const usuario = Api.usuario();
  const nombre = usuario.nombre || "Usuario";
  const iniciales = nombre.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("") || "U";
  const paginas = [
    ["panel.html", "Inicio", Ico.inicio, "inicio panel"],
    ["produccion.html", "Producción y Operaciones", Ico.grafica, "produccion operaciones lotes trazabilidad"],
    ["logistica.html", "Logística y Distribución", Ico.camion, "logistica distribucion pedidos transporte rutas"],
    ["costos.html", "Costos y Rentabilidad", Ico.dinero, "costos rentabilidad energia consumo tarifas"],
    ["reportes.html", "Análisis y Reportes", Ico.barras, "analisis reportes alertas huella carbono"],
  ];
  const actual = location.pathname.split("/").pop() || "panel.html";
  const norm = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

  const main = document.querySelector("main");
  document.getElementById("nav")?.remove();

  const shell = document.createElement("div");
  shell.className = "app-shell";
  shell.innerHTML = `
    <aside class="sidebar oscuro" aria-label="Navegación principal">
      <a class="marca" href="panel.html" aria-label="SmartOps inicio">
        <img src="img/smartops-mark-light.svg" alt="">
        <span class="marca-texto"><span class="wordmark">Smart<b>Ops</b></span>
        <span class="marca-lema">Operaciones Inteligentes para PyMEs Industriales</span></span>
      </a>
      <nav class="nav-lista">
        ${paginas.map(([h, t, i]) => `<a class="nav-item ${h === actual ? "activo" : ""}" href="${h}">${i}<span>${t}</span></a>`).join("")}
      </nav>
      <div class="nav-sep"></div>
      <button class="nav-item pequeno" id="btn-salir" type="button">${Ico.salir}<span>Cerrar sesión</span></button>
      <p class="sidebar-lema">Optimiza hoy,<br>crece mañana.</p>
    </aside>
    <div class="velo" id="velo"></div>
    <div class="contenido">
      <header class="topbar">
        <button class="menu-btn" id="btn-menu" type="button" aria-label="Abrir menú">${Ico.menu}</button>
        <form class="buscador" id="form-buscar-global" role="search">
          ${Ico.buscar}<input id="buscar-global" type="search" placeholder="Buscar en la plataforma..." aria-label="Buscar en la plataforma" autocomplete="off">
        </form>
        <div class="topbar-der">
          <a class="campana" id="campana" href="reportes.html" aria-label="Alertas">${Ico.campana}<i></i></a>
          <div class="usuario-chip"><div class="avatar">${iniciales}</div><span>Hola, ${nombre.split(/\s+/)[0]}</span></div>
        </div>
      </header>
    </div>`;

  document.body.prepend(shell);
  const contenido = shell.querySelector(".contenido");
  if (main) contenido.appendChild(main);
  const pie = document.createElement("footer");
  pie.className = "pie-pagina";
  pie.innerHTML = "<span>SmartOps · Operaciones Inteligentes para PyMEs Industriales</span><span>Tu operación, en una sola plataforma.</span>";
  contenido.appendChild(pie);

  document.getElementById("btn-salir").onclick = Api.salir;
  const alternar = () => shell.classList.toggle("menu-abierto");
  document.getElementById("btn-menu").onclick = alternar;
  document.getElementById("velo").onclick = alternar;

  // · Búsqueda rápida: un código de lote abre su consulta; un texto lleva al módulo que coincida.
  document.getElementById("form-buscar-global").addEventListener("submit", (e) => {
    e.preventDefault();
    const campo = document.getElementById("buscar-global");
    const q = campo.value.trim();
    if (!q) return;
    if (/^lot-/i.test(q)) { location.href = "modulo.html?codigo=" + encodeURIComponent(q.toUpperCase()); return; }
    const hallado = paginas.find(([, t, , k]) => norm(t + " " + k).includes(norm(q)));
    if (hallado) { location.href = hallado[0]; return; }
    campo.value = "";
    campo.placeholder = "Sin resultados. Prueba «logística» o un código LOT-…";
  });

  // · Resumen del panel: se pide una sola vez y se comparte (el panel lo reutiliza).
  let cache;
  window.resumenPanel = () => (cache ||= Api.get("/panel/resumen"));
  resumenPanel()
    .then((r) => { if (r.alertas && r.alertas.length) document.getElementById("campana").classList.add("con-alertas"); })
    .catch(() => {});
})();
