const form = document.getElementById("form-login");
const msg = document.getElementById("msg");
const campoNombre = document.getElementById("campo-nombre");
const btnModo = document.getElementById("btn-modo");
let registro = false;

if (Api.token()) location.href = "panel.html";

btnModo.addEventListener("click", () => {
  registro = !registro;
  campoNombre.style.display = registro ? "flex" : "none";
  document.getElementById("btn-enviar").textContent = registro ? "Crear cuenta" : "Ingresar";
  btnModo.textContent = registro ? "Ya tengo cuenta" : "Crear una cuenta";
  msg.textContent = "";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.textContent = "";
  const f = new FormData(form);
  try {
    const d = registro
      ? await Api.post("/auth/registro", { nombre: f.get("nombre"), email: f.get("email"), password: f.get("password") })
      : await Api.post("/auth/login", { email: f.get("email"), password: f.get("password") });
    Api.guardarSesion(d);
    location.href = "panel.html";
  } catch (err) {
    msg.textContent = err.message;
  }
});