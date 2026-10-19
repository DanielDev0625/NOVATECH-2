const form = document.getElementById("form-login");
const msg = document.getElementById("msg");
const campoNombre = document.getElementById("campo-nombre");
const btnModo = document.getElementById("btn-modo");
const btnEnviar = document.getElementById("btn-enviar");
const pass = document.getElementById("password");
const btnVer = document.getElementById("btn-ver");
let registro = false;

// · Pone los iconos SVG en los marcadores data-ico.
document.querySelectorAll("[data-ico]").forEach((el) => { el.innerHTML = Ico[el.dataset.ico] || ""; });
btnVer.innerHTML = Ico.ojo;

if (Api.token()) location.href = "panel.html";

btnVer.addEventListener("click", () => {
  const oculto = pass.type === "password";
  pass.type = oculto ? "text" : "password";
  btnVer.innerHTML = oculto ? Ico.ojoCerrado : Ico.ojo;
  btnVer.setAttribute("aria-label", oculto ? "Ocultar contraseña" : "Mostrar contraseña");
});

btnModo.addEventListener("click", () => {
  registro = !registro;
  campoNombre.style.display = registro ? "block" : "none";
  document.getElementById("titulo").textContent = registro ? "Crear cuenta" : "Bienvenido";
  document.getElementById("subtitulo").textContent = registro
    ? "Regístrate para empezar a usar la plataforma" : "Inicia sesión para acceder a tu plataforma";
  document.getElementById("txt-enviar").textContent = registro ? "Crear cuenta" : "Iniciar sesión";
  document.getElementById("txt-modo").textContent = registro ? "¿Ya tienes una cuenta?" : "¿No tienes una cuenta?";
  btnModo.textContent = registro ? "Iniciar sesión" : "Crear una cuenta";
  pass.autocomplete = registro ? "new-password" : "current-password";
  msg.textContent = "";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.textContent = "";
  const f = new FormData(form);
  const email = String(f.get("email") || "").trim();
  const password = String(f.get("password") || "");
  if (!email || !password) { msg.textContent = "Escribe tu correo y tu contraseña."; return; }
  if (registro && !String(f.get("nombre") || "").trim()) { msg.textContent = "Escribe tu nombre."; return; }
  btnEnviar.disabled = true;
  try {
    const d = registro
      ? await Api.post("/auth/registro", { nombre: f.get("nombre"), email, password })
      : await Api.post("/auth/login", { email, password });
    Api.guardarSesion(d, document.getElementById("recordar").checked);
    location.href = "panel.html";
  } catch (err) {
    msg.textContent = err.message;
    btnEnviar.disabled = false;
  }
});
