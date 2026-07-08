"use strict";

const API_CMI = "/api/cmi";
const TIPOS_CMI = [
  ["financiera", "Financiera"],
  ["clientes", "Clientes"],
  ["procesos", "Procesos internos"],
  ["aprendizaje", "Aprendizaje"],
];

let empresaCmiId = 1;
let perspectivas = [];
let graficosCmi = {};

// jsonFetch delega en el helper compartido apiFetch (comun.js).
const jsonFetch = apiFetch;

function porcentaje(valor) {
  if (valor === null || valor === undefined || Number.isNaN(Number(valor))) return "N/D";
  return `${(Number(valor) * 100).toFixed(2)}%`;
}

async function cargarCmi() {
  empresaCmiId = Number(document.querySelector("#cmi_empresa_id").value);
  perspectivas = await jsonFetch(`${API_CMI}/perspectivas?empresa_id=${empresaCmiId}`);
  renderTablero();
}

function renderTablero() {
  const tablero = document.querySelector("#tablero-cmi");
  for (const grafico of Object.values(graficosCmi)) grafico.destroy();
  graficosCmi = {};
  tablero.replaceChildren();
  for (const [tipo, label] of TIPOS_CMI) {
    const perspectiva = perspectivas.find((p) => p.tipo === tipo);
    const tarjeta = tarjetaPerspectiva(tipo, label, perspectiva);
    tablero.append(tarjeta);
    if (perspectiva) renderGraficoPerspectiva(perspectiva);
  }
}

function tarjetaPerspectiva(tipo, label, perspectiva) {
  const section = document.createElement("section");
  section.className = "panel tarjeta-cmi";

  const header = document.createElement("div");
  header.className = "panel-encabezado";
  const h2 = document.createElement("h2");
  h2.textContent = label;
  header.append(h2);
  if (!perspectiva) {
    header.append(boton("Crear perspectiva", () => crearPerspectiva(tipo, label)));
    section.append(header, mensaje("Crea la perspectiva para agregar objetivos e indicadores."));
    return section;
  }
  section.append(header, formObjetivo(perspectiva));

  if (perspectiva.objetivos.length === 0) {
    section.append(mensaje("Agrega el primer objetivo de control."));
    return section;
  }
  for (const objetivo of perspectiva.objetivos) {
    section.append(bloqueObjetivo(objetivo));
  }
  section.append(contenedorGrafico(perspectiva.id));
  return section;
}

function bloqueObjetivo(objetivo) {
  const cont = document.createElement("div");
  cont.className = "objetivo-cmi";
  const h3 = document.createElement("h3");
  h3.textContent = objetivo.descripcion;
  cont.append(h3, formIndicador(objetivo));

  if (objetivo.indicadores.length === 0) {
    cont.append(mensaje("Agrega indicadores para este objetivo."));
    return cont;
  }

  const tabla = document.createElement("table");
  tabla.className = "tabla-editable tabla-cmi";
  tabla.append(cabeceraIndicadores());
  const tbody = document.createElement("tbody");
  for (const indicador of objetivo.indicadores) {
    tbody.append(filaIndicador(indicador));
  }
  tabla.append(tbody);
  cont.append(tabla);
  return cont;
}

function cabeceraIndicadores() {
  const thead = document.createElement("thead");
  const tr = document.createElement("tr");
  for (const texto of ["Indicador", "Meta", "Sentido", "Ultimo valor", "Estado", "Periodo", "Valor", "Acciones"]) {
    const th = document.createElement("th");
    th.textContent = texto;
    tr.append(th);
  }
  thead.append(tr);
  return thead;
}

function filaIndicador(indicador) {
  const tr = document.createElement("tr");
  const ultima = indicador.mediciones.at(-1) || null;
  const estado = document.createElement("td");
  estado.id = `estado-cmi-${indicador.id}`;
  estado.textContent = ultima ? "Calculando" : "Sin medicion";
  if (ultima) evaluarUltima(indicador.id, ultima.id);

  tr.append(
    celdaTexto(indicador.nombre),
    celdaTexto(indicador.meta),
    celdaTexto(indicador.sentido),
    celdaTexto(ultima ? ultima.valor : "N/D"),
    estado,
    celdaInput(`cmi-periodo-${indicador.id}`, "", "text", "2026-07"),
    celdaInput(`cmi-valor-${indicador.id}`, 0, "number"),
    celdaAcciones([
      boton("Registrar", () => registrarMedicion(indicador.id)),
      boton("Eliminar", () => eliminarIndicador(indicador.id), "peligro"),
    ]),
  );
  return tr;
}

function contenedorGrafico(perspectivaId) {
  const div = document.createElement("div");
  div.className = "grafico grafico-cmi";
  const canvas = document.createElement("canvas");
  canvas.id = `grafico-cmi-${perspectivaId}`;
  div.append(canvas);
  return div;
}

function formObjetivo(perspectiva) {
  const form = document.createElement("form");
  form.className = "form-inline form-cmi";
  form.append(
    labelInput(`obj-${perspectiva.id}`, "Objetivo", "text"),
    boton("Agregar objetivo", null),
  );
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await agregarObjetivo(perspectiva.id);
  });
  return form;
}

function formIndicador(objetivo) {
  const form = document.createElement("form");
  form.className = "form-inline form-cmi";
  form.append(
    labelInput(`ind-nombre-${objetivo.id}`, "Indicador", "text"),
    labelInput(`ind-meta-${objetivo.id}`, "Meta", "number"),
    labelSelect(`ind-sentido-${objetivo.id}`, "Sentido", [["directo", "Directo"], ["inverso", "Inverso"]]),
    boton("Agregar indicador", null),
  );
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await agregarIndicador(objetivo.id);
  });
  return form;
}

function labelInput(id, texto, tipo) {
  const label = document.createElement("label");
  label.textContent = texto;
  const input = document.createElement("input");
  input.id = id;
  input.type = tipo;
  if (tipo === "number") {
    input.step = "0.01";
  }
  label.append(input);
  return label;
}

function labelSelect(id, texto, opciones) {
  const label = document.createElement("label");
  label.textContent = texto;
  const select = document.createElement("select");
  select.id = id;
  for (const [valor, nombre] of opciones) {
    const option = document.createElement("option");
    option.value = valor;
    option.textContent = nombre;
    select.append(option);
  }
  label.append(select);
  return label;
}

function celdaTexto(texto) {
  const td = document.createElement("td");
  td.textContent = texto;
  return td;
}

function celdaInput(id, valor, tipo = "text", placeholder = "") {
  const td = document.createElement("td");
  const input = document.createElement("input");
  input.id = id;
  input.type = tipo;
  input.value = valor;
  input.placeholder = placeholder;
  if (tipo === "number") input.step = "0.01";
  td.append(input);
  return td;
}

function celdaAcciones(botones) {
  const td = document.createElement("td");
  const div = document.createElement("div");
  div.className = "acciones";
  div.append(...botones);
  td.append(div);
  return td;
}

function boton(texto, fn, clase = "") {
  const b = document.createElement("button");
  b.type = fn ? "button" : "submit";
  b.textContent = texto;
  b.className = clase;
  if (fn) b.onclick = conManejoErrores(fn, texto);
  return b;
}

function mensaje(texto) {
  const p = document.createElement("p");
  p.className = "mensaje-vacio";
  p.textContent = texto;
  return p;
}

async function crearPerspectiva(tipo, nombre) {
  await jsonFetch(`${API_CMI}/perspectivas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ empresa_id: empresaCmiId, tipo, nombre }),
  });
  await cargarCmi();
}

async function agregarObjetivo(perspectivaId) {
  const descripcion = document.querySelector(`#obj-${perspectivaId}`).value;
  if (!descripcion.trim()) return marcarCampoInvalido(`#obj-${perspectivaId}`, "El objetivo es obligatorio.");
  await jsonFetch(`${API_CMI}/perspectivas/${perspectivaId}/objetivos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ descripcion }),
  });
  await cargarCmi();
}

async function agregarIndicador(objetivoId) {
  const nombre = document.querySelector(`#ind-nombre-${objetivoId}`).value;
  const meta = Number(document.querySelector(`#ind-meta-${objetivoId}`).value || 0);
  const sentido = document.querySelector(`#ind-sentido-${objetivoId}`).value;
  if (!nombre.trim()) return marcarCampoInvalido(`#ind-nombre-${objetivoId}`, "El indicador es obligatorio.");
  if (!validarNumeroNoNegativo(`#ind-meta-${objetivoId}`, "La meta debe ser mayor o igual a cero.")) return;
  await jsonFetch(`${API_CMI}/objetivos/${objetivoId}/indicadores`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, meta, sentido }),
  });
  await cargarCmi();
}

async function registrarMedicion(indicadorId) {
  const periodo = document.querySelector(`#cmi-periodo-${indicadorId}`).value;
  const valor = Number(document.querySelector(`#cmi-valor-${indicadorId}`).value || 0);
  if (!periodo.trim()) return marcarCampoInvalido(`#cmi-periodo-${indicadorId}`, "El periodo es obligatorio.");
  if (!validarNumeroNoNegativo(`#cmi-valor-${indicadorId}`, "El valor debe ser mayor o igual a cero.")) return;
  await jsonFetch(`${API_CMI}/indicadores/${indicadorId}/mediciones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ periodo, valor }),
  });
  await cargarCmi();
}

async function eliminarIndicador(indicadorId) {
  if (!confirm("Eliminar indicador CMI?")) return;
  await jsonFetch(`${API_CMI}/indicadores/${indicadorId}`, { method: "DELETE" });
  await cargarCmi();
}

async function evaluarUltima(indicadorId, medicionId) {
  const resultado = await jsonFetch(`${API_CMI}/mediciones/${medicionId}/semaforo`);
  const celda = document.querySelector(`#estado-cmi-${indicadorId}`);
  if (!celda) return;
  celda.textContent = `${resultado.estado} ${porcentaje(resultado.cumplimiento)}`;
  celda.className = `semaforo ${resultado.estado.toLowerCase()}`;
}

function renderGraficoPerspectiva(perspectiva) {
  const indicadores = perspectiva.objetivos.flatMap((objetivo) => objetivo.indicadores);
  const conMediciones = indicadores.filter((indicador) => indicador.mediciones.length > 0);
  if (conMediciones.length === 0) return;

  const labels = [];
  for (const indicador of conMediciones) {
    for (const medicion of indicador.mediciones) {
      if (!labels.includes(medicion.periodo)) labels.push(medicion.periodo);
    }
  }

  const colores = ["#1565c0", "#2e7d32", "#f9a825", "#c62828", "#607d8b"];
  const datasets = conMediciones.map((indicador, idx) => ({
    label: indicador.nombre,
    data: labels.map((periodo) => {
      const medicion = indicador.mediciones.find((m) => m.periodo === periodo);
      return medicion ? medicion.valor : null;
    }),
    borderColor: colores[idx % colores.length],
    backgroundColor: colores[idx % colores.length],
    tension: 0.25,
    spanGaps: true,
  }));

  const canvas = document.querySelector(`#grafico-cmi-${perspectiva.id}`);
  if (!canvas) return;
  graficosCmi[perspectiva.id] = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

document.querySelector("#form-contexto-cmi").addEventListener("submit", conManejoErrores(async (e) => {
  e.preventDefault();
  if (!validarNumeroNoNegativo("#cmi_empresa_id", "La empresa debe ser un numero valido.")) return;
  await cargarCmi();
}, "Error al cargar CMI"));

cargarCmi().catch((err) => notificar("Error al cargar CMI: " + err.message, "error"));
