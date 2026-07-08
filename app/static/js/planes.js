"use strict";

const API_PLANES = "/api/planes";
const TIPOS_PLAN = [
  ["financiero", "Financiero"],
  ["marketing", "Marketing"],
  ["operaciones", "Operaciones"],
  ["mejoras", "Mejoras"],
  ["tecnologico", "Tecnologico"],
  ["compras", "Compras"],
  ["control", "Control"],
];

let empresaId = 1;
let tipoActivo = "financiero";
let planes = [];
let totales = null;
let graficoFinanciero = null;

// jsonFetch delega en el helper compartido apiFetch (comun.js).
const jsonFetch = apiFetch;

function dinero(valor) {
  return Number(valor || 0).toLocaleString("es-EC", {
    style: "currency",
    currency: "USD",
  });
}

function porcentaje(valor) {
  if (valor === null || valor === undefined || Number.isNaN(Number(valor))) return "N/D";
  return `${(Number(valor) * 100).toFixed(2)}%`;
}

function planActivo() {
  return planes.find((p) => p.tipo === tipoActivo) || null;
}

function etiquetaTipo(tipo) {
  const item = TIPOS_PLAN.find(([valor]) => valor === tipo);
  return item ? item[1] : tipo;
}

async function cargarPlanes() {
  empresaId = Number(document.querySelector("#empresa_id").value);
  planes = await jsonFetch(`${API_PLANES}?empresa_id=${empresaId}`);
  totales = await jsonFetch(`${API_PLANES}/consolidado/totales?empresa_id=${empresaId}`);
  renderTabs();
  renderPlan();
}

function renderTabs() {
  const cont = document.querySelector("#tabs-planes");
  cont.replaceChildren();
  for (const [tipo, label] of TIPOS_PLAN) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.className = tipo === tipoActivo ? "activo" : "";
    b.onclick = () => {
      tipoActivo = tipo;
      renderTabs();
      renderPlan();
    };
    cont.append(b);
  }
}

function renderPlan() {
  const plan = planActivo();
  document.querySelector("#titulo-plan").textContent = `Plan ${etiquetaTipo(tipoActivo)}`;
  document.querySelector("#btn-crear-plan").hidden = Boolean(plan);
  document.querySelector("#form-estrategia").hidden = !plan;
  document.querySelector("#total-empresa").textContent = dinero(totales?.total_costo || 0);

  const totalPlan = totales?.planes?.find((p) => p.tipo === tipoActivo)?.total_costo || 0;
  document.querySelector("#total-plan").textContent = dinero(totalPlan);

  const cuerpo = document.querySelector("#tabla-planes tbody");
  cuerpo.replaceChildren();
  renderIndicadores(plan);
  if (!plan) {
    cuerpo.append(filaMensaje("Crea este plan para agregar estrategias y actividades."));
    return;
  }
  if (plan.estrategias.length === 0) {
    cuerpo.append(filaMensaje("Agrega la primera estrategia de este plan."));
    return;
  }

  for (const estrategia of plan.estrategias) {
    cuerpo.append(filaEstrategia(estrategia));
    for (const actividad of estrategia.actividades) {
      cuerpo.append(filaActividad(actividad));
    }
    cuerpo.append(filaNuevaActividad(estrategia));
  }
}

function renderIndicadores(plan) {
  const cuerpo = document.querySelector("#tabla-indicadores tbody");
  const resumen = document.querySelector("#resumen-ponderaciones");
  cuerpo.replaceChildren();

  if (!plan) {
    resumen.textContent = "Sin plan";
    resumen.className = "estado-ponderacion";
    cuerpo.append(filaMensaje("Crea este plan para agregar indicadores.", 11));
    return;
  }
  if (plan.estrategias.length === 0) {
    resumen.textContent = "Sin estrategias";
    resumen.className = "estado-ponderacion";
    cuerpo.append(filaMensaje("Agrega estrategias para capturar indicadores.", 11));
    return;
  }

  let totalIndicadores = 0;
  for (const estrategia of plan.estrategias) {
    totalIndicadores += estrategia.indicadores.length;
    cuerpo.append(filaNuevaIndicador(estrategia));
    for (const indicador of estrategia.indicadores) {
      cuerpo.append(filaIndicador(estrategia, indicador));
    }
  }

  resumen.textContent = `${totalIndicadores} indicadores`;
  resumen.className = "estado-ponderacion";
}

function filaMensaje(texto, colSpan = 8) {
  const tr = document.createElement("tr");
  const td = document.createElement("td");
  td.colSpan = colSpan;
  td.className = "mensaje-vacio";
  td.textContent = texto;
  tr.append(td);
  return tr;
}

function filaEstrategia(estrategia) {
  const tr = document.createElement("tr");
  tr.className = "fila-estrategia";
  tr.append(
    celdaInput(`tipo-${estrategia.id}`, estrategia.tipo_estrategia || ""),
    celdaInput(`desc-${estrategia.id}`, estrategia.descripcion),
    celdaTexto(""),
    celdaTexto(""),
    celdaTexto(""),
    celdaTexto(totalEstrategia(estrategia)),
    celdaTexto(""),
    celdaAcciones([
      boton("Guardar", () => guardarEstrategia(estrategia)),
      boton("Eliminar", () => eliminarEstrategia(estrategia.id), "peligro"),
    ]),
  );
  return tr;
}

function filaActividad(actividad) {
  const tr = document.createElement("tr");
  tr.append(
    celdaTexto(""),
    celdaTexto(""),
    celdaInput(`act-desc-${actividad.id}`, actividad.descripcion),
    celdaInput(`act-resp-${actividad.id}`, actividad.responsable || ""),
    celdaInput(`act-tiempo-${actividad.id}`, actividad.tiempo || ""),
    celdaInput(`act-costo-${actividad.id}`, actividad.costo ?? 0, "number"),
    celdaInput(`act-cuenta-${actividad.id}`, actividad.tipo_cuenta || ""),
    celdaAcciones([
      boton("Guardar", () => guardarActividad(actividad)),
      boton("Eliminar", () => eliminarActividad(actividad.id), "peligro"),
    ]),
  );
  return tr;
}

function filaNuevaActividad(estrategia) {
  const tr = document.createElement("tr");
  tr.append(
    celdaTexto(""),
    celdaTexto(""),
    celdaInput(`new-desc-${estrategia.id}`, "", "text", "Actividad"),
    celdaInput(`new-resp-${estrategia.id}`, "", "text", "Responsable"),
    celdaInput(`new-tiempo-${estrategia.id}`, "", "text", "Tiempo"),
    celdaInput(`new-costo-${estrategia.id}`, 0, "number"),
    celdaInput(`new-cuenta-${estrategia.id}`, "", "text", "Cuenta"),
    celdaAcciones([boton("Agregar", () => agregarActividad(estrategia.id))]),
  );
  return tr;
}

function filaNuevaIndicador(estrategia) {
  const tr = document.createElement("tr");
  tr.className = "fila-nuevo-indicador";
  tr.append(
    celdaTexto(estrategia.descripcion),
    celdaInput(`new-kpi-tipo-${estrategia.id}`, "", "text", "Tipo"),
    celdaInput(`new-kpi-nombre-${estrategia.id}`, "", "text", "Indicador"),
    celdaInput(`new-kpi-formula-${estrategia.id}`, "", "text", "Formula"),
    celdaInput(`new-kpi-frecuencia-${estrategia.id}`, "", "text", "Frecuencia"),
    celdaInput(`new-kpi-peso-${estrategia.id}`, 0, "number"),
    celdaTexto(""),
    celdaTexto(""),
    celdaTexto(""),
    celdaTexto(""),
    celdaAcciones([
      boton("Agregar", () => agregarIndicador(estrategia.id)),
      boton("Validar", () => validarPonderaciones(estrategia.id), "sec"),
    ]),
  );
  return tr;
}

function filaIndicador(estrategia, indicador) {
  const tr = document.createElement("tr");
  tr.append(
    celdaTexto(estrategia.descripcion),
    celdaInput(`kpi-tipo-${indicador.id}`, indicador.tipo || ""),
    celdaInput(`kpi-nombre-${indicador.id}`, indicador.nombre),
    celdaInput(`kpi-formula-${indicador.id}`, indicador.formula || ""),
    celdaInput(`kpi-frecuencia-${indicador.id}`, indicador.frecuencia || ""),
    celdaInput(`kpi-peso-${indicador.id}`, indicador.ponderacion ?? 0, "number"),
    celdaInput(`kpi-periodo-${indicador.id}`, "", "text", "Periodo"),
    celdaInput(`kpi-num-${indicador.id}`, 0, "number"),
    celdaInput(`kpi-den-${indicador.id}`, 1, "number"),
    celdaTextoResultado(indicador.id),
    celdaAcciones([
      boton("Guardar", () => guardarIndicador(indicador)),
      boton("Calcular", () => calcularIndicador(indicador), "sec"),
      boton("Eliminar", () => eliminarIndicador(indicador.id), "peligro"),
    ]),
  );
  return tr;
}

function totalEstrategia(estrategia) {
  return dinero(estrategia.actividades.reduce((suma, a) => suma + Number(a.costo || 0), 0));
}

function celdaTexto(texto) {
  const td = document.createElement("td");
  td.textContent = texto;
  return td;
}

function celdaTextoResultado(indicadorId) {
  const td = document.createElement("td");
  td.id = `kpi-res-${indicadorId}`;
  td.textContent = "N/D";
  return td;
}

function celdaInput(id, valor, tipo = "text", placeholder = "") {
  const td = document.createElement("td");
  const input = document.createElement("input");
  input.id = id;
  input.type = tipo;
  input.value = valor;
  input.placeholder = placeholder;
  if (tipo === "number") {
    input.min = "0";
    input.step = "0.01";
  }
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
  b.type = "button";
  b.textContent = texto;
  b.className = clase;
  b.onclick = conManejoErrores(fn, texto);
  return b;
}

async function crearPlan() {
  try {
    await jsonFetch(API_PLANES, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ empresa_id: empresaId, tipo: tipoActivo, estrategias: [] }),
    });
    await cargarPlanes();
  } catch (err) {
    notificar("Error al crear plan: " + err.message, "error");
  }
}

document.querySelector("#form-contexto").addEventListener("submit", conManejoErrores(async (e) => {
  e.preventDefault();
  if (!validarNumeroNoNegativo("#empresa_id", "La empresa debe ser un numero valido.")) return;
  await cargarPlanes();
}, "Error al cargar planes"));

document.querySelector("#btn-crear-plan").addEventListener("click", crearPlan);
document.querySelector("#btn-dashboard-demo").addEventListener("click", cargarValoresDemo);

document.querySelector("#form-estrategia").addEventListener("submit", async (e) => {
  e.preventDefault();
  const plan = planActivo();
  if (!plan) return;
  if (!validarTextoObligatorio("#descripcion_estrategia", "La estrategia es obligatoria.")) return;
  const payload = {
    tipo_estrategia: document.querySelector("#tipo_estrategia").value || null,
    descripcion: document.querySelector("#descripcion_estrategia").value,
  };
  try {
    await jsonFetch(`${API_PLANES}/${plan.id}/estrategias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    document.querySelector("#tipo_estrategia").value = "";
    document.querySelector("#descripcion_estrategia").value = "";
    await cargarPlanes();
  } catch (err) {
    notificar("Error al agregar estrategia: " + err.message, "error");
  }
});

async function guardarEstrategia(estrategia) {
  if (!validarTextoObligatorio(`#desc-${estrategia.id}`, "La estrategia es obligatoria.")) return;
  const payload = {
    tipo_estrategia: document.querySelector(`#tipo-${estrategia.id}`).value || null,
    descripcion: document.querySelector(`#desc-${estrategia.id}`).value,
  };
  await jsonFetch(`${API_PLANES}/estrategias/${estrategia.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await cargarPlanes();
}

async function eliminarEstrategia(id) {
  if (!confirm("Eliminar estrategia?")) return;
  await jsonFetch(`${API_PLANES}/estrategias/${id}`, { method: "DELETE" });
  await cargarPlanes();
}

async function agregarActividad(estrategiaId) {
  const descripcion = document.querySelector(`#new-desc-${estrategiaId}`).value;
  if (!descripcion.trim()) {
    marcarCampoInvalido(`#new-desc-${estrategiaId}`, "La actividad es obligatoria.");
    return;
  }
  if (!validarNumeroNoNegativo(`#new-costo-${estrategiaId}`, "El costo debe ser mayor o igual a cero.")) return;
  const payload = {
    descripcion,
    responsable: document.querySelector(`#new-resp-${estrategiaId}`).value || null,
    tiempo: document.querySelector(`#new-tiempo-${estrategiaId}`).value || null,
    costo: Number(document.querySelector(`#new-costo-${estrategiaId}`).value || 0),
    tipo_cuenta: document.querySelector(`#new-cuenta-${estrategiaId}`).value || null,
  };
  await jsonFetch(`${API_PLANES}/estrategias/${estrategiaId}/actividades`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await cargarPlanes();
}

async function guardarActividad(actividad) {
  if (!validarTextoObligatorio(`#act-desc-${actividad.id}`, "La actividad es obligatoria.")) return;
  if (!validarNumeroNoNegativo(`#act-costo-${actividad.id}`, "El costo debe ser mayor o igual a cero.")) return;
  const payload = {
    descripcion: document.querySelector(`#act-desc-${actividad.id}`).value,
    responsable: document.querySelector(`#act-resp-${actividad.id}`).value || null,
    tiempo: document.querySelector(`#act-tiempo-${actividad.id}`).value || null,
    costo: Number(document.querySelector(`#act-costo-${actividad.id}`).value || 0),
    tipo_cuenta: document.querySelector(`#act-cuenta-${actividad.id}`).value || null,
  };
  await jsonFetch(`${API_PLANES}/actividades/${actividad.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await cargarPlanes();
}

async function eliminarActividad(id) {
  if (!confirm("Eliminar actividad?")) return;
  await jsonFetch(`${API_PLANES}/actividades/${id}`, { method: "DELETE" });
  await cargarPlanes();
}

async function agregarIndicador(estrategiaId) {
  const nombre = document.querySelector(`#new-kpi-nombre-${estrategiaId}`).value;
  if (!nombre.trim()) {
    marcarCampoInvalido(`#new-kpi-nombre-${estrategiaId}`, "El indicador es obligatorio.");
    return;
  }
  if (!validarNumeroNoNegativo(`#new-kpi-peso-${estrategiaId}`, "La ponderacion debe ser mayor o igual a cero.")) return;
  const payload = {
    tipo: document.querySelector(`#new-kpi-tipo-${estrategiaId}`).value || null,
    nombre,
    formula: document.querySelector(`#new-kpi-formula-${estrategiaId}`).value || null,
    frecuencia: document.querySelector(`#new-kpi-frecuencia-${estrategiaId}`).value || null,
    ponderacion: Number(document.querySelector(`#new-kpi-peso-${estrategiaId}`).value || 0),
  };
  await jsonFetch(`${API_PLANES}/estrategias/${estrategiaId}/indicadores`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await cargarPlanes();
}

async function guardarIndicador(indicador) {
  if (!validarTextoObligatorio(`#kpi-nombre-${indicador.id}`, "El indicador es obligatorio.")) return;
  if (!validarNumeroNoNegativo(`#kpi-peso-${indicador.id}`, "La ponderacion debe ser mayor o igual a cero.")) return;
  const payload = {
    tipo: document.querySelector(`#kpi-tipo-${indicador.id}`).value || null,
    nombre: document.querySelector(`#kpi-nombre-${indicador.id}`).value,
    formula: document.querySelector(`#kpi-formula-${indicador.id}`).value || null,
    frecuencia: document.querySelector(`#kpi-frecuencia-${indicador.id}`).value || null,
    ponderacion: Number(document.querySelector(`#kpi-peso-${indicador.id}`).value || 0),
  };
  await jsonFetch(`${API_PLANES}/indicadores/${indicador.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await cargarPlanes();
}

async function eliminarIndicador(id) {
  if (!confirm("Eliminar indicador?")) return;
  await jsonFetch(`${API_PLANES}/indicadores/${id}`, { method: "DELETE" });
  await cargarPlanes();
}

async function calcularIndicador(indicador) {
  if (!validarNumeroNoNegativo(`#kpi-num-${indicador.id}`, "El numerador debe ser mayor o igual a cero.")) return;
  if (!validarNumeroNoNegativo(`#kpi-den-${indicador.id}`, "El denominador debe ser mayor o igual a cero.")) return;
  const payload = {
    numerador: Number(document.querySelector(`#kpi-num-${indicador.id}`).value || 0),
    denominador: Number(document.querySelector(`#kpi-den-${indicador.id}`).value || 0),
    periodo: document.querySelector(`#kpi-periodo-${indicador.id}`).value || null,
  };
  const resultado = await jsonFetch(`${API_PLANES}/indicadores/${indicador.id}/calcular`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const celda = document.querySelector(`#kpi-res-${indicador.id}`);
  celda.textContent = resultado.valor === null ? "N/D" : porcentaje(resultado.valor);
}

async function validarPonderaciones(estrategiaId) {
  const resultado = await jsonFetch(`${API_PLANES}/estrategias/${estrategiaId}/indicadores/ponderaciones`);
  const resumen = document.querySelector("#resumen-ponderaciones");
  resumen.textContent = `Estrategia ${estrategiaId}: ${porcentaje(resultado.total_ponderacion)} (${resultado.valido ? "OK" : "revisar"})`;
  resumen.className = resultado.valido ? "estado-ponderacion ok" : "estado-ponderacion alerta";
}

document.querySelector("#form-dashboard").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validarNumeroNoNegativo("#ventas_base", "Ventas base debe ser mayor o igual a cero.")) return;
  if (!validarNumeroNoNegativo("#costos_base", "Costos base debe ser mayor o igual a cero.")) return;
  await calcularDashboardFinanciero();
});

function valorNumericoOpcional(id) {
  const valor = document.querySelector(id).value;
  return valor === "" ? null : Number(valor);
}

function cargarValoresDemo() {
  document.querySelector("#ventas_base").value = "100000";
  document.querySelector("#costos_base").value = "58000";
  document.querySelector("#costos_fijos").value = "22000";
  document.querySelector("#costos_variables").value = "36000";
}

async function calcularDashboardFinanciero() {
  const params = new URLSearchParams({
    empresa_id: String(empresaId),
    ventas_base: document.querySelector("#ventas_base").value,
    costos_base: document.querySelector("#costos_base").value,
  });
  const opcionales = {
    gastos_operativos_base: valorNumericoOpcional("#gastos_operativos_base"),
    inversion_inicial: valorNumericoOpcional("#inversion_inicial"),
    costos_fijos: valorNumericoOpcional("#costos_fijos"),
    costos_variables: valorNumericoOpcional("#costos_variables"),
  };
  for (const [clave, valor] of Object.entries(opcionales)) {
    if (valor !== null) params.set(clave, String(valor));
  }

  try {
    const dashboard = await jsonFetch(`${API_PLANES}/dashboard/financiero?${params}`);
    renderDashboardFinanciero(dashboard);
  } catch (err) {
    notificar("Error al calcular dashboard financiero: " + err.message, "error");
  }
}

function renderDashboardFinanciero(dashboard) {
  document.querySelector("#dashboard-financiero").hidden = false;
  renderMetricas(dashboard);
  renderPremisas(dashboard.premisas, dashboard.total_planes);
  renderTablaProyeccion(dashboard.proyeccion);
  renderGraficoFinanciero(dashboard.proyeccion);
}

function renderMetricas(dashboard) {
  const cont = document.querySelector("#metricas-financieras");
  cont.replaceChildren(
    metrica("VAN", dinero(dashboard.metricas.van)),
    metrica("TIR", porcentaje(dashboard.metricas.tir)),
    metrica("Payback", dashboard.metricas.payback === null ? "N/D" : `${dashboard.metricas.payback} años`),
    metrica("Punto equilibrio", dashboard.metricas.punto_equilibrio === null ? "N/D" : dinero(dashboard.metricas.punto_equilibrio)),
  );
}

function renderPremisas(premisas, totalPlanes) {
  const cont = document.querySelector("#premisas-financieras");
  cont.replaceChildren(
    textoResumen("Inflacion", porcentaje(premisas.inflacion)),
    textoResumen("Crecimiento ventas", porcentaje(premisas.crecimiento_ventas)),
    textoResumen("Impuestos", porcentaje(premisas.impuestos)),
    textoResumen("WACC", porcentaje(premisas.wacc)),
    textoResumen("Total planes", dinero(totalPlanes)),
  );
}

function metrica(nombre, valor) {
  const div = document.createElement("div");
  div.className = "metrica";
  const label = document.createElement("strong");
  label.textContent = nombre;
  const dato = document.createElement("span");
  dato.textContent = valor;
  div.append(label, dato);
  return div;
}

function textoResumen(nombre, valor) {
  const frag = document.createDocumentFragment();
  const label = document.createElement("strong");
  label.textContent = `${nombre}:`;
  const dato = document.createElement("span");
  dato.textContent = valor;
  frag.append(label, dato);
  return frag;
}

function renderTablaProyeccion(proyeccion) {
  const cuerpo = document.querySelector("#tabla-proyeccion tbody");
  cuerpo.replaceChildren();
  for (const anio of proyeccion) {
    const tr = document.createElement("tr");
    tr.append(
      celdaTexto(anio.anio),
      celdaTexto(dinero(anio.ventas)),
      celdaTexto(dinero(anio.costos)),
      celdaTexto(dinero(anio.utilidad_bruta)),
      celdaTexto(dinero(anio.gastos_operativos)),
      celdaTexto(dinero(anio.ebitda)),
      celdaTexto(dinero(anio.utilidad_neta)),
    );
    cuerpo.append(tr);
  }
}

function renderGraficoFinanciero(proyeccion) {
  if (graficoFinanciero) graficoFinanciero.destroy();
  const ctx = document.querySelector("#grafico-financiero").getContext("2d");
  graficoFinanciero = new Chart(ctx, {
    type: "line",
    data: {
      labels: proyeccion.map((a) => `Año ${a.anio}`),
      datasets: [
        { label: "Ventas", data: proyeccion.map((a) => a.ventas), borderColor: "#1565c0", backgroundColor: "rgba(21,101,192,.12)" },
        { label: "EBITDA", data: proyeccion.map((a) => a.ebitda), borderColor: "#2e7d32", backgroundColor: "rgba(46,125,50,.12)" },
        { label: "Utilidad neta", data: proyeccion.map((a) => a.utilidad_neta), borderColor: "#f9a825", backgroundColor: "rgba(249,168,37,.12)" },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: { y: { beginAtZero: true } },
    },
  });
}

cargarPlanes().catch((err) => notificar("Error al cargar planes: " + err.message, "error"));
