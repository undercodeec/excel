"use strict";
// Cliente del módulo Matrices: consume /api/matrices y dibuja con Chart.js.

const API = "/api/matrices";
let grafico = null;

// jsonFetch delega en el helper compartido apiFetch (comun.js).
const jsonFetch = apiFetch;

// ---------- Listado ----------
async function cargarMatrices() {
  const cuerpo = document.querySelector("#tabla-matrices tbody");
  cuerpo.innerHTML = "";
  const matrices = await jsonFetch(API);
  for (const m of matrices) {
    const tr = document.createElement("tr");
    for (const val of [m.id, m.tipo, m.nombre]) {
      const c = document.createElement("td");
      c.textContent = val;
      tr.append(c);
    }
    const td = document.createElement("td");
    const bCalc = document.createElement("button");
    bCalc.textContent = "Calcular";
    bCalc.onclick = conManejoErrores(() => calcular(m.id, m.tipo), "Error al calcular");
    const bDel = document.createElement("button");
    bDel.textContent = "Eliminar";
    bDel.className = "peligro";
    bDel.onclick = conManejoErrores(() => eliminar(m.id), "Error al eliminar");
    td.append(bCalc, " ", bDel);
    tr.append(td);
    cuerpo.append(tr);
  }
}

// ---------- Crear ----------
document.querySelector("#form-matriz").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validarNumeroNoNegativo("#empresa_id", "La empresa debe ser un numero valido.")) return;
  if (!validarTextoObligatorio("#nombre", "El nombre de la matriz es obligatorio.")) return;
  const payload = {
    empresa_id: Number(document.querySelector("#empresa_id").value),
    tipo: document.querySelector("#tipo").value,
    nombre: document.querySelector("#nombre").value,
    factores: [],
  };
  try {
    await jsonFetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    document.querySelector("#nombre").value = "";
    await cargarMatrices();
    notificar("Matriz creada.", "exito");
  } catch (err) { notificar("Error al crear: " + err.message, "error"); }
});

async function eliminar(id) {
  if (!confirm("¿Eliminar matriz " + id + "?")) return;
  await jsonFetch(`${API}/${id}`, { method: "DELETE" });
  await cargarMatrices();
}

// ---------- Cálculo + gráfico ----------
async function calcular(id, tipo) {
  const panel = document.querySelector("#panel-detalle");
  const detalle = document.querySelector("#detalle");
  panel.hidden = false;
  try {
    const r = await jsonFetch(`${API}/${id}/calculo`);
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(r, null, 2);
    detalle.replaceChildren(pre);
    dibujar(tipo, r);
  } catch (err) {
    const p = document.createElement("p");
    p.className = "peligro";
    p.textContent = "Error: " + err.message;
    detalle.replaceChildren(p);
    destruirGrafico();
  }
}

function destruirGrafico() { if (grafico) { grafico.destroy(); grafico = null; } }

function dibujar(tipo, r) {
  destruirGrafico();
  const ctx = document.querySelector("#lienzo").getContext("2d");
  if (tipo === "peyea") return dibujarPeyea(ctx, r);
  if (tipo === "cinco_fuerzas") return dibujarRadar(ctx, r);
  if (tipo === "mpc") return dibujarBarras(ctx, r);
  if (tipo === "ansoff") return dibujarAnsoff(ctx, r);
  // Ponderados: barras de resultado por factor
  if (r.factores) return dibujarBarras(ctx, r);
}

function dibujarPeyea(ctx, r) {
  grafico = new Chart(ctx, {
    type: "scatter",
    data: { datasets: [
      { label: "Vector (" + r.cuadrante + ")", data: [{ x: 0, y: 0 }, { x: r.x, y: r.y }],
        showLine: true, borderColor: "#1565c0", backgroundColor: "#1565c0" },
    ]},
    options: {
      scales: {
        x: { min: -6, max: 6, grid: { color: "#ccc" }, title: { display: true, text: "FI + VC" } },
        y: { min: -6, max: 6, grid: { color: "#ccc" }, title: { display: true, text: "FF + EE" } },
      },
      plugins: { title: { display: true, text: "PEYEA — Cuadrante: " + r.cuadrante } },
    },
  });
}

function dibujarRadar(ctx, r) {
  const f = r.factores || [];
  grafico = new Chart(ctx, {
    type: "radar",
    data: {
      labels: f.map((x) => x.descripcion || x.categoria),
      datasets: [{ label: "Puntaje", data: f.map((x) => x.resultado ?? x.puntaje ?? 0),
        borderColor: "#1565c0", backgroundColor: "rgba(21,101,192,.2)" }],
    },
  });
}

function dibujarBarras(ctx, r) {
  const f = r.factores || [];
  grafico = new Chart(ctx, {
    type: "bar",
    data: {
      labels: f.map((x) => x.descripcion || x.categoria),
      datasets: [{ label: "Resultado", data: f.map((x) => x.resultado ?? x.puntaje ?? 0),
        backgroundColor: "#1565c0" }],
    },
  });
}

function dibujarAnsoff(ctx, r) {
  // Cuadrícula 2×2 conceptual; muestra factores como dispersión etiquetada
  grafico = new Chart(ctx, {
    type: "scatter",
    data: { datasets: [{ label: "Ansoff", data: [{ x: 0, y: 0 }], backgroundColor: "#1565c0" }] },
    options: {
      scales: {
        x: { min: 0, max: 2, title: { display: true, text: "Productos (actual → nuevo)" } },
        y: { min: 0, max: 2, title: { display: true, text: "Mercados (actual → nuevo)" } },
      },
      plugins: { title: { display: true, text: "Ansoff 2×2" } },
    },
  });
}

cargarMatrices().catch((err) => notificar("Error al cargar matrices: " + err.message, "error"));
