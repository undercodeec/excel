"use strict";

const API_DASHBOARD = "/api/dashboard";

const ETIQUETAS_TIPO_MATRIZ = {
  holmes: "Holmes", foda_cuali: "FODA cualitativo", foda_cuanti: "FODA cuantitativo",
  efi: "EFI", efe: "EFE", cadena_valor: "Cadena de valor", aoor: "AOOR",
  aprovechabilidad: "Aprovechabilidad", cinco_fuerzas: "5 Fuerzas", mpc: "MPC",
  ansoff: "Ansoff", pestel: "PESTEL", peyea: "PEYEA", madi: "MADI", made: "MADE",
};

let graficoSemaforos = null;

// jsonFetch delega en el helper compartido apiFetch (comun.js).
const jsonFetch = apiFetch;

function moneda(valor) {
  return Number(valor || 0).toLocaleString("es-EC", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function cargarDashboard() {
  const empresaId = Number(document.querySelector("#dash_empresa_id").value);
  if (!validarNumeroNoNegativo("#dash_empresa_id", "La empresa debe ser un numero valido.")) return;
  const errorEl = document.querySelector("#dash_error");
  errorEl.hidden = true;
  try {
    const data = await jsonFetch(`${API_DASHBOARD}/general?empresa_id=${empresaId}`);
    renderDashboard(data);
  } catch (e) {
    errorEl.textContent = `No se pudo cargar el dashboard: ${e.message}`;
    errorEl.hidden = false;
    document.querySelector("#tablero-dashboard").replaceChildren();
  }
}

function tarjeta(titulo) {
  const section = document.createElement("section");
  section.className = "panel tarjeta-dashboard";
  const h2 = document.createElement("h2");
  h2.textContent = titulo;
  section.append(h2);
  return section;
}

function filaMetrica(etiqueta, valor) {
  const p = document.createElement("p");
  p.className = "dash-metrica";
  const spanE = document.createElement("span");
  spanE.className = "metrica-etiqueta";
  spanE.textContent = etiqueta;
  const spanV = document.createElement("span");
  spanV.className = "metrica-valor";
  spanV.textContent = valor;
  p.append(spanE, spanV);
  return p;
}

function listaPorTipo(mapa, formato) {
  const ul = document.createElement("ul");
  ul.className = "lista-tipos";
  const entradas = Object.entries(mapa || {});
  if (entradas.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Sin datos";
    ul.append(li);
    return ul;
  }
  for (const [clave, valor] of entradas) {
    const li = document.createElement("li");
    li.textContent = `${formato(clave)}: ${valor}`;
    ul.append(li);
  }
  return ul;
}

function renderDashboard(data) {
  const tablero = document.querySelector("#tablero-dashboard");
  if (graficoSemaforos) { graficoSemaforos.destroy(); graficoSemaforos = null; }
  tablero.replaceChildren();

  const cabecera = document.createElement("div");
  cabecera.className = "panel-encabezado";
  const titulo = document.createElement("h2");
  titulo.className = "dashboard-empresa";
  titulo.textContent = `${data.empresa_nombre} (empresa #${data.empresa_id})`;
  const exportar = document.createElement("a");
  exportar.className = "boton-export";
  exportar.href = `${API_DASHBOARD.replace("/dashboard", "/export")}/excel?empresa_id=${data.empresa_id}`;
  exportar.textContent = "Exportar a Excel";
  cabecera.append(titulo, exportar);
  tablero.append(cabecera);

  const grid = document.createElement("div");
  grid.className = "dashboard-grid";
  tablero.append(grid);

  // Matrices
  const tMat = tarjeta("Matrices");
  tMat.append(filaMetrica("Total de matrices", data.matrices.total));
  tMat.append(listaPorTipo(data.matrices.por_tipo, (t) => ETIQUETAS_TIPO_MATRIZ[t] || t));
  grid.append(tMat);

  // Planes
  const tPlan = tarjeta("Planes");
  tPlan.append(filaMetrica("Planes", data.planes.total_planes));
  tPlan.append(filaMetrica("Estrategias", data.planes.total_estrategias));
  tPlan.append(filaMetrica("Actividades", data.planes.total_actividades));
  tPlan.append(filaMetrica("Costo total", moneda(data.planes.total_costo)));
  tPlan.append(listaPorTipo(data.planes.total_por_tipo, (t) => t));
  grid.append(tPlan);

  // KPI
  const tKpi = tarjeta("KPI tácticos");
  tKpi.append(filaMetrica("Indicadores", data.kpi.total_indicadores));
  grid.append(tKpi);

  // CMI
  const tCmi = tarjeta("CMI");
  tCmi.append(filaMetrica("Perspectivas", data.cmi.total_perspectivas));
  tCmi.append(filaMetrica("Objetivos", data.cmi.total_objetivos));
  tCmi.append(filaMetrica("Indicadores", data.cmi.total_indicadores));
  tCmi.append(filaMetrica("Mediciones", data.cmi.total_mediciones));
  const canvas = document.createElement("canvas");
  tCmi.append(canvas);
  grid.append(tCmi);

  // Trazabilidad
  const tTraz = tarjeta("Trazabilidad");
  tTraz.append(filaMetrica("Estrategias con matriz origen", data.trazabilidad.estrategias_con_matriz));
  tTraz.append(filaMetrica("Indicadores CMI con KPI", data.trazabilidad.indicadores_cmi_con_kpi));
  grid.append(tTraz);

  renderGraficoSemaforos(canvas, data.cmi.semaforos);
}

function renderGraficoSemaforos(canvas, s) {
  const total = s.verde + s.amarillo + s.rojo + s.sin_medicion;
  if (total === 0) {
    const p = document.createElement("p");
    p.textContent = "Aún no hay indicadores CMI.";
    canvas.replaceWith(p);
    return;
  }
  graficoSemaforos = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Verde", "Amarillo", "Rojo", "Sin medición"],
      datasets: [{
        data: [s.verde, s.amarillo, s.rojo, s.sin_medicion],
        backgroundColor: ["#2e9e4f", "#e8b53a", "#d1493f", "#9aa0a6"],
      }],
    },
    options: { plugins: { legend: { position: "bottom" } } },
  });
}

document.querySelector("#form-contexto-dashboard").addEventListener("submit", (e) => {
  e.preventDefault();
  conManejoErrores(cargarDashboard, "Error al cargar dashboard")();
});

cargarDashboard().catch((err) => notificar("Error al cargar dashboard: " + err.message, "error"));
