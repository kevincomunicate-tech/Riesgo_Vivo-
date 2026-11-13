// Gráficos interactivos con Chart.js. Los datos vienen del CSV filtrado
// (calculados con pandas en services.chart_data) a través de json_script.
(function () {
  const dataEl = document.getElementById("chart-data");
  if (!dataEl || typeof Chart === "undefined") return;
  const data = JSON.parse(dataEl.textContent);

  const AZUL = "#0d6efd", ROJO = "#dc3545", GRIS = "#6c757d";
  const fmt = new Intl.NumberFormat("es-CO");
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
  Chart.defaults.color = GRIS;
  Chart.defaults.maintainAspectRatio = false;

  // --- Top de eventos: barras horizontales, cambia de métrica y filtra la tabla ---
  const topCtx = document.getElementById("chart-top");
  let filtroActivo = null;
  const metricaLabel = { eventos: "Eventos", personas: "Personas afectadas" };

  const topChart = new Chart(topCtx, {
    type: "bar",
    data: {
      labels: data.top.labels,
      datasets: [{ label: metricaLabel.eventos, data: data.top.eventos, backgroundColor: AZUL, borderRadius: 4 }],
    },
    options: {
      indexAxis: "y",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmt.format(c.raw)}` } },
      },
      scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
      onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
      onClick: (e, els) => {
        if (!els.length) return;
        const i = els[0].index;
        filtrarTabla(filtroActivo === data.top.keys[i] ? null : data.top.keys[i], data.top.labels[i]);
      },
    },
  });

  document.querySelectorAll("[data-metrica]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const m = btn.dataset.metrica;
      document.querySelectorAll("[data-metrica]").forEach((b) => b.classList.toggle("active", b === btn));
      topChart.data.datasets[0].data = data.top[m];
      topChart.data.datasets[0].label = metricaLabel[m];
      colorMetrica = m === "eventos" ? AZUL : ROJO;
      pintarTop();
    });
  });

  let colorMetrica = AZUL;
  function pintarTop() {
    // Resalta la barra seleccionada y atenúa las demás.
    topChart.data.datasets[0].backgroundColor = data.top.keys.map((k) =>
      !filtroActivo || k === filtroActivo ? colorMetrica : "#ced4da");
    topChart.update();
  }

  function filtrarTabla(evento, etiqueta) {
    filtroActivo = evento;
    document.querySelectorAll("tr[data-evento]").forEach((tr) => {
      tr.classList.toggle("d-none", !!evento && tr.dataset.evento !== evento);
    });
    const aviso = document.getElementById("filtro-tabla");
    aviso.classList.toggle("d-none", !evento);
    document.getElementById("filtro-tabla-evento").textContent = etiqueta || "";
    pintarTop();
  }
  document.getElementById("quitar-filtro-tabla")?.addEventListener("click", () => filtrarTabla(null));

  // --- Evolución mensual: línea de eventos + barras de personas (dos ejes) ---
  new Chart(document.getElementById("chart-mensual"), {
    data: {
      labels: data.mensual.labels,
      datasets: [
        { type: "line", label: "Eventos", data: data.mensual.eventos, borderColor: AZUL, backgroundColor: AZUL, tension: 0.3, yAxisID: "y" },
        { type: "bar", label: "Personas afectadas", data: data.mensual.personas, backgroundColor: "rgba(220,53,69,.25)", yAxisID: "y1" },
      ],
    },
    options: {
      interaction: { mode: "index", intersect: false },
      plugins: { tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmt.format(c.raw)}` } } },
      scales: {
        y: { beginAtZero: true, position: "left", title: { display: true, text: "Eventos" }, ticks: { precision: 0 } },
        y1: { beginAtZero: true, position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "Personas" } },
      },
    },
  });

  // --- Distribución del impacto ---
  new Chart(document.getElementById("chart-distribucion"), {
    type: "bar",
    data: {
      labels: data.distribucion.labels,
      datasets: [{ label: "Eventos", data: data.distribucion.eventos, backgroundColor: AZUL, borderRadius: 4 }],
    },
    options: {
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { title: (c) => `${c[0].label} personas afectadas`, label: (c) => `Eventos: ${fmt.format(c.raw)}` } },
      },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });
})();
