const Api = {
  // · La sesión vive en localStorage ("Recordarme") o en sessionStorage (se cierra con el navegador).
  token: () => localStorage.getItem("token") || sessionStorage.getItem("token"),
  usuario: () => JSON.parse(localStorage.getItem("usuario") || sessionStorage.getItem("usuario") || "{}"),

  async req(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    if (Api.token()) headers.Authorization = "Bearer " + Api.token();
    const r = await fetch("/api" + path, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
    });
    if (r.status === 401 && !path.startsWith("/auth/")) {
      Api.salir();
      throw new Error("Sesión expirada");
    }
    const data = await r.json().catch(() => null);
    if (!r.ok) {
      const d = data && data.detail;
      throw new Error(typeof d === "string" ? d : "Revisa los datos ingresados");
    }
    return data;
  },

  get: (p) => Api.req("GET", p),
  post: (p, b) => Api.req("POST", p, b),
  patch: (p, b) => Api.req("PATCH", p, b),

  async descargar(path) {
    const r = await fetch("/api" + path, {
      headers: Api.token() ? { Authorization: "Bearer " + Api.token() } : {},
    });
    if (!r.ok) throw new Error("No se pudo generar el archivo");
    window.open(URL.createObjectURL(await r.blob()), "_blank");
  },

  guardarSesion(d, recordar = true) {
    Api.limpiar();
    const almacen = recordar ? localStorage : sessionStorage;
    almacen.setItem("token", d.token);
    almacen.setItem("usuario", JSON.stringify(d.usuario));
  },

  limpiar() {
    ["token", "usuario"].forEach((k) => { localStorage.removeItem(k); sessionStorage.removeItem(k); });
  },

  salir() {
    Api.limpiar();
    location.href = "login.html";
  },
};