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
    const bInf = document.createElement("button");
    bInf.textContent = "Informe";
    bInf.style.background = "#2e7d32";
    bInf.onclick = conManejoErrores(() => verInforme(m.id), "Error al cargar informe");
    const bDel = document.createElement("button");
    bDel.textContent = "Eliminar";
    bDel.className = "peligro";
    bDel.onclick = conManejoErrores(() => eliminar(m.id), "Error al eliminar");
    td.append(bCalc, " ", bInf, " ", bDel);
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

// ---------- Informe ----------
function esc(val) {
  if (val == null) return "—";
  return String(val)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

document.querySelector("#btn-cerrar-informe").addEventListener("click", () => {
  document.querySelector("#panel-informe").hidden = true;
});

async function verInforme(id) {
  const panel = document.querySelector("#panel-informe");
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth" });

  const inf = await jsonFetch(`${API}/${id}/informe`);

  // --- Empresa ---
  const emp = inf.empresa;
  document.querySelector("#inf-empresa").innerHTML = `
    <h3 style="margin:0 0 .5rem">${esc(emp.nombre)}</h3>
    <p style="margin:.2rem 0"><strong>Período:</strong> ${esc(emp.periodo)} &nbsp;|&nbsp; <strong>Moneda:</strong> ${esc(emp.moneda)}</p>
    ${emp.mision ? `<p style="margin:.2rem 0"><strong>Misión:</strong> ${esc(emp.mision)}</p>` : ""}
    ${emp.vision ? `<p style="margin:.2rem 0"><strong>Visión:</strong> ${esc(emp.vision)}</p>` : ""}
  `;

  // --- Cálculo ---
  const calc = inf.calculo;
  let htmlCalc = `<h3>Resultado del cálculo — <em>${esc(inf.matriz_tipo.toUpperCase())}</em>: ${esc(inf.matriz_nombre)}</h3>`;

  if (calc.cuadrante) {
    // PEYEA
    htmlCalc += `<table class="tabla-editable"><tbody>
      <tr><td>FF</td><td>${esc(calc.ff?.toFixed(2))}</td></tr>
      <tr><td>FI</td><td>${esc(calc.fi?.toFixed(2))}</td></tr>
      <tr><td>EE</td><td>${esc(calc.ee?.toFixed(2))}</td></tr>
      <tr><td>VC</td><td>${esc(calc.vc?.toFixed(2))}</td></tr>
      <tr><td><strong>X (FI+VC)</strong></td><td>${esc(calc.x?.toFixed(2))}</td></tr>
      <tr><td><strong>Y (FF+EE)</strong></td><td>${esc(calc.y?.toFixed(2))}</td></tr>
      <tr><td><strong>Cuadrante</strong></td><td>${esc(calc.cuadrante)}</td></tr>
    </tbody></table>`;
  } else if (calc.total !== undefined) {
    // Ponderados / PESTEL
    htmlCalc += `<p><strong>Total ponderado:</strong> ${esc(calc.total?.toFixed(3))}</p>`;
    if (calc.factores?.length) {
      htmlCalc += `<table class="tabla-editable">
        <thead><tr><th>Factor</th><th>Peso</th><th>Calificación</th><th>Resultado</th></tr></thead>
        <tbody>
          ${calc.factores.map(f => `<tr>
            <td>${esc(f.descripcion ?? f.categoria)}</td>
            <td>${esc(f.peso?.toFixed(3))}</td>
            <td>${esc((f.calificacion ?? f.puntaje)?.toFixed(2))}</td>
            <td><strong>${esc((f.resultado ?? f.puntaje)?.toFixed(3))}</strong></td>
          </tr>`).join("")}
        </tbody>
      </table>`;
    }
  } else if (calc.filas) {
    // Holmes
    htmlCalc += `<table class="tabla-editable">
      <thead><tr><th>Factor</th><th>Total</th><th>Orden</th></tr></thead>
      <tbody>
        ${calc.filas.map(f => `<tr><td>${esc(f.factor)}</td><td>${esc(f.total)}</td><td>${esc(f.orden)}</td></tr>`).join("")}
      </tbody>
    </table>`;
  }
  document.querySelector("#inf-calculo").innerHTML = htmlCalc;

  // --- Estrategias vinculadas ---
  const estDiv = document.querySelector("#inf-estrategias");
  if (!inf.estrategias_vinculadas?.length) {
    estDiv.innerHTML = `<p style="color:#888;margin-top:1rem">No hay estrategias vinculadas a esta matriz aún.</p>`;
    return;
  }

  let htmlEst = `<h3 style="margin-top:1.5rem">Estrategias y planes derivados</h3>`;
  for (const est of inf.estrategias_vinculadas) {
    htmlEst += `
      <div class="panel" style="margin-bottom:1rem;background:#f9f9f9">
        <p style="margin:0 0 .3rem"><strong>Plan:</strong> ${esc(est.plan_tipo.toUpperCase())} &nbsp;|&nbsp;
           <strong>Estrategia #${esc(est.estrategia_id)}:</strong> ${esc(est.descripcion)}</p>
        ${est.tipo_estrategia ? `<p style="margin:0 0 .5rem;color:#555">Tipo: ${esc(est.tipo_estrategia)}</p>` : ""}
        ${est.actividades?.length ? `
          <details open>
            <summary><strong>Actividades (${esc(est.actividades.length)})</strong></summary>
            <table class="tabla-editable" style="margin-top:.5rem">
              <thead><tr><th>Descripción</th><th>Responsable</th><th>Tiempo</th><th>Costo</th></tr></thead>
              <tbody>
                ${est.actividades.map(a => `<tr>
                  <td>${esc(a.descripcion)}</td>
                  <td>${esc(a.responsable)}</td>
                  <td>${esc(a.tiempo)}</td>
                  <td>${a.costo != null ? esc(a.costo.toLocaleString()) : "—"}</td>
                </tr>`).join("")}
              </tbody>
            </table>
          </details>` : ""}
        ${est.kpis?.length ? `
          <details style="margin-top:.5rem">
            <summary><strong>KPIs (${esc(est.kpis.length)})</strong></summary>
            <ul style="margin:.5rem 0 0 1rem">
              ${est.kpis.map(k => `<li>${esc(k.nombre)}${k.formula ? ` — <em>${esc(k.formula)}</em>` : ""}
                ${k.indicadores_cmi?.length ? ` → CMI: ${k.indicadores_cmi.map(i => esc(i.nombre)).join(", ")}` : ""}</li>`).join("")}
            </ul>
          </details>` : ""}
      </div>`;
  }
  estDiv.innerHTML = htmlEst;
}

cargarMatrices().catch((err) => notificar("Error al cargar matrices: " + err.message, "error"));
