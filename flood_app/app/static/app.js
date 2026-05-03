const $ = (id) => document.getElementById(id);

let levelChart = null;
let rateChart = null;

function bannerStyle(level){
  const banner = $("alertBanner");
  banner.style.borderColor = "rgba(255,255,255,0.09)";
  banner.style.background = "linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05))";

  if(level === "HIGH"){
    banner.style.borderColor = "rgba(251,113,133,0.55)";
    banner.style.background = "linear-gradient(180deg, rgba(251,113,133,0.20), rgba(255,255,255,0.05))";
  } else if(level === "MEDIUM"){
    banner.style.borderColor = "rgba(251,191,36,0.55)";
    banner.style.background = "linear-gradient(180deg, rgba(251,191,36,0.18), rgba(255,255,255,0.05))";
  } else if(level === "LOW"){
    banner.style.borderColor = "rgba(96,165,250,0.55)";
    banner.style.background = "linear-gradient(180deg, rgba(96,165,250,0.18), rgba(255,255,255,0.05))";
  } else {
    banner.style.borderColor = "rgba(45,212,191,0.35)";
    banner.style.background = "linear-gradient(180deg, rgba(45,212,191,0.14), rgba(255,255,255,0.05))";
  }
}

function fmt(num, digits=1){
  if(num === null || num === undefined || Number.isNaN(num)) return "—";
  return Number(num).toFixed(digits);
}

function shortTime(iso){
  try{ return new Date(iso).toLocaleTimeString(); }
  catch{ return "—"; }
}

function computeRiseRateSeries(series){
  const out = [];
  for(let i=1; i<series.length; i++){
    const t1 = new Date(series[i-1].t_iso).getTime();
    const t2 = new Date(series[i].t_iso).getTime();
    const dtMin = (t2 - t1) / 60000.0;
    if(dtMin <= 0) continue;
    const r = (series[i].water_level_cm - series[i-1].water_level_cm) / dtMin;
    out.push({ t_iso: series[i].t_iso, rate: r });
  }
  return out;
}

function ensureCharts(series, thresholds){
  if(!series || series.length < 2 || typeof Chart === 'undefined') return;

  const labels = series.map(p => shortTime(p.t_iso));
  const levelData = series.map(p => p.water_level_cm);

  const rr = computeRiseRateSeries(series);
  const rrLabels = rr.map(p => shortTime(p.t_iso));
  const rrData = rr.map(p => p.rate);

  const warning = thresholds?.warning_cm ?? 0;
  const danger = thresholds?.danger_cm ?? 0;

  if(!levelChart){
    levelChart = new Chart($("levelChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          { data: levelData, borderColor: "rgba(96,165,250,0.95)", backgroundColor: "rgba(96,165,250,0.10)", fill: true, tension: 0.25, pointRadius: 0 },
          { data: labels.map(() => warning), borderColor: "rgba(251,191,36,0.85)", borderDash: [6,6], pointRadius: 0, tension: 0 },
          { data: labels.map(() => danger), borderColor: "rgba(251,113,133,0.85)", borderDash: [6,6], pointRadius: 0, tension: 0 },
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { ticks: { color: "rgba(255,255,255,0.55)" } } }
      }
    });
  } else {
    levelChart.data.labels = labels;
    levelChart.data.datasets[0].data = levelData;
    levelChart.data.datasets[1].data = labels.map(() => warning);
    levelChart.data.datasets[2].data = labels.map(() => danger);
    levelChart.update();
  }

  if(!rateChart){
    rateChart = new Chart($("rateChart"), {
      type: "line",
      data: {
        labels: rrLabels,
        datasets: [
          { data: rrData, borderColor: "rgba(45,212,191,0.95)", backgroundColor: "rgba(45,212,191,0.08)", fill: true, tension: 0.25, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { ticks: { color: "rgba(255,255,255,0.55)" } } }
      }
    });
  } else {
    rateChart.data.labels = rrLabels;
    rateChart.data.datasets[0].data = rrData;
    rateChart.update();
  }
}

async function refresh(){
  try{
    const res = await fetch("/api/status", { cache: "no-store" });
    const json = await res.json();

    if(!json.ok){
      $("alertLevel").textContent = "NO ALERT";
      $("alertReason").textContent = json.message || "No data";
      bannerStyle("NO_ALERT");
      return;
    }

    const d = json.data;
    const level = d.alert.level;

    $("alertLevel").textContent = level.replace("_", " ");
    $("alertReason").textContent = d.alert.reason;
    bannerStyle(level);

    $("waterLevel").textContent = fmt(d.current_water_level_cm, 1);
    $("riseRate").textContent = fmt(d.rise_rate_cm_per_min, 2);

    $("thresholdHint").textContent =
      `Thresholds: warning ${fmt(d.thresholds.warning_cm,1)}cm • danger ${fmt(d.thresholds.danger_cm,1)}cm`;

    $("systemHint").textContent =
      `Sensor height ${fmt(d.system.sensor_height_cm,0)}cm • Drain height ${fmt(d.system.drain_height_cm,0)}cm`;

    $("lastUpdated").textContent = `Updated: ${new Date().toLocaleTimeString()}`;

    ensureCharts(d.series || [], d.thresholds || {});

  } catch(e){
    $("alertLevel").textContent = "NO ALERT";
    $("alertReason").textContent = "Backend not reachable.";
    bannerStyle("NO_ALERT");
  }
}

refresh();
setInterval(refresh, 3000);
