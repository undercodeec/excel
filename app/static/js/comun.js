"use strict";
// Utilidades compartidas por todos los modulos: errores API, validacion UI y toasts.

function traducirMensajeValidacion(mensaje) {
  const texto = String(mensaje);
  const reglas = [
    [/field required/i, "campo obligatorio"],
    [/input should be a valid integer/i, "debe ser un numero entero"],
    [/input should be a valid number/i, "debe ser un numero"],
    [/input should be greater than or equal to/i, "debe ser mayor o igual al minimo permitido"],
    [/input should be less than or equal to/i, "debe ser menor o igual al maximo permitido"],
    [/string should have at least/i, "debe completar el texto requerido"],
    [/value is not a valid enumeration member/i, "opcion no permitida"],
  ];
  const regla = reglas.find(([patron]) => patron.test(texto));
  return regla ? regla[1] : texto;
}

function formatearErrorApi(cuerpo) {
  if (cuerpo === null || cuerpo === undefined) return null;
  const detail = cuerpo.detail !== undefined ? cuerpo.detail : cuerpo;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const mensajes = detail.map((err) => {
      const loc = Array.isArray(err.loc)
        ? err.loc.filter((x) => x !== "body" && x !== "query" && x !== "path")
        : [];
      const campo = loc.join(" > ");
      const msg = traducirMensajeValidacion(err.msg || "valor invalido");
      return campo ? `${campo}: ${msg}` : msg;
    });
    return mensajes.join("; ");
  }

  try {
    return JSON.stringify(detail);
  } catch (_) {
    return String(detail);
  }
}

function mensajeError(err) {
  if (!err) return "Error inesperado.";
  return err.message || String(err);
}

function notificar(mensaje, tipo = "info") {
  let contenedor = document.querySelector("#notificaciones");
  if (!contenedor) {
    contenedor = document.createElement("div");
    contenedor.id = "notificaciones";
    contenedor.setAttribute("aria-live", "polite");
    document.body.append(contenedor);
  }
  const n = document.createElement("div");
  n.className = `notificacion notificacion-${tipo}`;
  n.setAttribute("role", tipo === "error" ? "alert" : "status");
  n.textContent = mensaje;
  n.addEventListener("click", () => n.remove());
  contenedor.append(n);
  setTimeout(() => n.remove(), tipo === "error" ? 7000 : 4000);
}

function marcarCampoInvalido(selector, mensaje) {
  const campo = typeof selector === "string" ? document.querySelector(selector) : selector;
  if (!campo) return false;
  campo.classList.add("campo-invalido");
  if (mensaje) campo.setCustomValidity(mensaje);
  campo.reportValidity();
  campo.addEventListener("input", () => {
    campo.classList.remove("campo-invalido");
    campo.setCustomValidity("");
  }, { once: true });
  return false;
}

function validarTextoObligatorio(selector, mensaje) {
  const campo = document.querySelector(selector);
  if (!campo || String(campo.value || "").trim()) return true;
  return marcarCampoInvalido(campo, mensaje || "Campo obligatorio.");
}

function validarNumeroNoNegativo(selector, mensaje) {
  const campo = document.querySelector(selector);
  if (!campo) return true;
  const valor = Number(campo.value);
  if (Number.isFinite(valor) && valor >= 0) return true;
  return marcarCampoInvalido(campo, mensaje || "Debe ingresar un numero mayor o igual a cero.");
}

function conManejoErrores(fn, contexto = "Operacion") {
  return async (...args) => {
    try {
      return await fn(...args);
    } catch (err) {
      notificar(`${contexto}: ${mensajeError(err)}`, "error");
      return null;
    }
  };
}

async function apiFetch(url, opciones) {
  const r = await fetch(url, opciones);
  if (!r.ok) {
    let msg = r.statusText;
    try {
      msg = formatearErrorApi(await r.json()) || msg;
    } catch (_) {}
    throw new Error(`HTTP ${r.status}: ${msg}`);
  }
  return r.status === 204 ? null : r.json();
}

window.addEventListener("unhandledrejection", (evento) => {
  const motivo = evento.reason;
  const mensaje = motivo && motivo.message ? motivo.message : String(motivo);
  notificar(mensaje, "error");
});
