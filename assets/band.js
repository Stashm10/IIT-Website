// Band page: daily histograms pooled into months / the whole year.
// Data: data/bands/<id>.json -> { band, days: [{date, files, sweeps, readings, sum, min, max,
//   mean, median, p10, p90, peak_bin_low, num_points, hist: {o, c}}] }
// Histogram bins are fixed (-150..+20 dBm, 0.5 dB), so summing daily counts is exact.

const BIN_LOW = -150, BIN_W = 0.5, NUM_BINS = 340;
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];
const YEAR = 2018;
const LAYOUT_BASE = {
  paper_bgcolor: "#fff", plot_bgcolor: "#fff",
  font: { color: "#1a1a1a", family: "Arial, Helvetica, sans-serif", size: 11 },
  margin: { t: 20, r: 20, b: 50, l: 65 },
  xaxis: { gridcolor: "#e8e8e8", zerolinecolor: "#ccc", linecolor: "#ccc" },
  yaxis: { gridcolor: "#e8e8e8", zerolinecolor: "#ccc", linecolor: "#ccc" },
};
const CONFIG = { responsive: true, displayModeBar: false };

// ---------- pooling ----------
function sumHist(days) {
  const out = new Array(NUM_BINS).fill(0);
  for (const d of days) d.hist.c.forEach((n, i) => { out[d.hist.o + i] += n; });
  return out;
}

// Quantile read off a histogram, interpolating linearly inside the bin.
function histQuantile(hist, total, q) {
  const target = q * total;
  let cum = 0;
  for (let i = 0; i < hist.length; i++) {
    if (hist[i] && cum + hist[i] >= target) return BIN_LOW + BIN_W * (i + (target - cum) / hist[i]);
    cum += hist[i];
  }
  return BIN_LOW + BIN_W * hist.length;
}

function pooledStats(days) {
  const hist = sumHist(days);
  const readings = days.reduce((a, d) => a + d.readings, 0);
  let peak = 0;
  hist.forEach((n, i) => { if (n > hist[peak]) peak = i; });
  return {
    exact: days.length === 1,
    days: days.length,
    sweeps: days.reduce((a, d) => a + d.sweeps, 0),
    readings,
    min: Math.min(...days.map(d => d.min)),
    max: Math.max(...days.map(d => d.max)),
    mean: days.reduce((a, d) => a + d.sum, 0) / readings,
    median: days.length === 1 ? days[0].median : histQuantile(hist, readings, 0.5),
    p10: days.length === 1 ? days[0].p10 : histQuantile(hist, readings, 0.1),
    p90: days.length === 1 ? days[0].p90 : histQuantile(hist, readings, 0.9),
    peak_bin_low: BIN_LOW + BIN_W * peak,
    hist,
  };
}

// ---------- helpers ----------
const pad = n => String(n).padStart(2, "0");
const fmt = (x, d = 1) => (x == null || Number.isNaN(x) ? "–" : x.toFixed(d));
const daysInMonth = m => new Date(YEAR, m, 0).getDate();
const monthOf = date => Number(date.slice(5, 7));
function longDate(date) {
  return `${MONTHS[monthOf(date) - 1]} ${Number(date.slice(8))}, ${YEAR}`;
}
function el(tag, attrs = {}, text) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k.startsWith("on")) e[k] = v; else e.setAttribute(k, v);
  }
  if (text != null) e.textContent = text;
  return e;
}

// ---------- state ----------
let DATA, BY_DATE, YEAR_STATS, X_RANGE;
// month: "all" | 1..12, quarter: null | 1..4 (only with month "all"), day: "YYYY-MM-DD" | null
let state = { month: "all", quarter: null, day: null };

const quarterMonths = q => [3 * q - 2, 3 * q - 1, 3 * q];
const daysInQuarter = q => quarterMonths(q).reduce((a, m) => a + daysInMonth(m), 0);
const quarterName = q => `Q${q} ${YEAR} (${MONTHS[3 * q - 3].slice(0, 3)}–${MONTHS[3 * q - 1].slice(0, 3)})`;
const isYearView = () => state.month === "all" && !state.quarter && !state.day;
const daysInMonths = months => DATA.days.filter(d => months.includes(monthOf(d.date)));

function readHash() {
  const h = location.hash.slice(1);
  let m;
  if ((m = h.match(/^(\d{4})-(\d{2})-(\d{2})$/)) && BY_DATE[h]) return { month: Number(m[2]), quarter: null, day: h };
  if ((m = h.match(/^(\d{4})-(\d{2})$/)) && Number(m[2]) >= 1 && Number(m[2]) <= 12) return { month: Number(m[2]), quarter: null, day: null };
  if ((m = h.match(/^(\d{4})-Q([1-4])$/i))) return { month: "all", quarter: Number(m[2]), day: null };
  return { month: "all", quarter: null, day: null };
}
function select(next) {
  state = { month: "all", quarter: null, day: null, ...next };
  const hash = state.day
    || (state.quarter ? `${YEAR}-Q${state.quarter}` : state.month === "all" ? "" : `${YEAR}-${pad(state.month)}`);
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname);
  render();
}
function selectedDays() {
  if (state.day) return [BY_DATE[state.day]];
  if (state.quarter) return daysInMonths(quarterMonths(state.quarter));
  if (state.month === "all") return DATA.days;
  return daysInMonths([state.month]);
}

// ---------- rendering ----------
function renderPicker() {
  const periods = document.getElementById("period-tabs");
  periods.replaceChildren(el("button", { class: "pick-btn", type: "button", "aria-pressed": String(isYearView()),
    onclick: () => select({}) }, `All ${YEAR}`));
  for (let q = 1; q <= 4; q++) {
    const n = daysInMonths(quarterMonths(q)).length;
    const b = el("button", { class: "pick-btn", type: "button", "aria-pressed": String(state.quarter === q),
      title: `${quarterName(q)}: ${n} of ${daysInQuarter(q)} days observed`,
      onclick: () => select({ quarter: q }) }, `Q${q}`);
    if (!n) b.disabled = true;
    periods.append(b);
  }

  const tabs = document.getElementById("month-tabs");
  tabs.replaceChildren();
  MONTHS.forEach((name, i) => {
    const m = i + 1;
    const n = daysInMonths([m]).length;
    const b = el("button", { class: "pick-btn", type: "button", "aria-pressed": String(state.month === m),
      title: `${n} of ${daysInMonth(m)} days observed`, onclick: () => select({ month: m }) }, name.slice(0, 3));
    if (!n) b.disabled = true;
    tabs.append(b);
  });

  const row = document.getElementById("day-row");
  const btns = document.getElementById("day-buttons");
  btns.replaceChildren();
  row.hidden = state.month === "all";
  if (state.month === "all") return;
  btns.append(el("button", { class: "pick-btn", type: "button", "aria-pressed": String(!state.day),
    onclick: () => select({ month: state.month }) }, "Whole month"));
  for (let d = 1; d <= daysInMonth(state.month); d++) {
    const date = `${YEAR}-${pad(state.month)}-${pad(d)}`;
    const b = el("button", { class: "pick-btn", type: "button", "aria-pressed": String(state.day === date),
      title: BY_DATE[date] ? longDate(date) : `${longDate(date)} — no data`,
      onclick: () => select({ month: state.month, day: date }) }, String(d));
    if (!BY_DATE[date]) b.disabled = true;
    btns.append(b);
  }
}

function selectionLabel() {
  if (state.day) return longDate(state.day);
  if (state.quarter) return quarterName(state.quarter);
  if (state.month === "all") return `All of ${YEAR}`;
  return `${MONTHS[state.month - 1]} ${YEAR}`;
}

function renderSummary(stats) {
  let sub;
  if (state.day) {
    const d = BY_DATE[state.day];
    sub = `${d.sweeps} sweeps · source file${d.files.length > 1 ? "s" : ""}: ${d.files.join(", ")}`;
  } else if (state.quarter) {
    sub = `${stats.days} of ${daysInQuarter(state.quarter)} days observed · ${stats.sweeps.toLocaleString()} sweeps pooled`;
  } else if (state.month === "all") {
    sub = `${stats.days} observed days · ${stats.sweeps.toLocaleString()} sweeps pooled`;
  } else {
    sub = `${stats.days} of ${daysInMonth(state.month)} days observed · ${stats.sweeps.toLocaleString()} sweeps pooled`;
  }
  document.getElementById("selection-title").textContent = selectionLabel();
  document.getElementById("selection-sub").textContent = sub;

  const approx = stats.exact ? "" : "≈";
  const binNote = stats.exact ? null : "from the pooled histogram (±0.5 dB)";
  const items = [
    { label: "Readings", value: stats.readings.toLocaleString() },
    { label: "Min Power", value: fmt(stats.min), unit: "dBm" },
    { label: "Max Power", value: fmt(stats.max), unit: "dBm" },
    { label: "Mean Power", value: fmt(stats.mean, 2), unit: "dBm" },
    { label: "Median", value: approx + fmt(stats.median, 2), unit: "dBm", note: binNote },
    { label: "10th percentile", value: approx + fmt(stats.p10, 2), unit: "dBm", note: binNote },
    { label: "90th percentile", value: approx + fmt(stats.p90, 2), unit: "dBm", note: binNote },
    { label: "Most common", value: fmt(stats.peak_bin_low), unit: "dBm",
      note: `fullest 0.5 dB bin (${fmt(stats.peak_bin_low)} to ${fmt(stats.peak_bin_low + BIN_W)})` },
  ];
  document.getElementById("stats-grid").innerHTML = items.map(it => `
    <div class="stat-item">
      <div class="stat-label">${it.label}</div>
      <div class="stat-value">${it.value}${it.unit ? `<span class="stat-unit">${it.unit}</span>` : ""}</div>
      ${it.note ? `<div class="stat-note">${it.note}</div>` : ""}
    </div>`).join("");
}

function renderHistogram(stats) {
  const x = stats.hist.map((_, i) => BIN_LOW + BIN_W * (i + 0.5));
  const pct = h => { const t = h.reduce((a, b) => a + b, 0); return h.map(n => (100 * n) / t); };
  const traces = [{
    x, y: pct(stats.hist), type: "bar", name: selectionLabel(),
    marker: { color: "#CC0000" },
    hovertemplate: "%{x:.2f} dBm — %{y:.2f}% of readings<extra></extra>",
  }];
  if (!isYearView()) {
    traces.push({
      x, y: pct(YEAR_STATS.hist), type: "scatter", mode: "lines", name: `All of ${YEAR}`,
      line: { color: "#555", width: 1.5, shape: "hvh" },
      hovertemplate: `%{x:.2f} dBm — %{y:.2f}% (all ${YEAR})<extra></extra>`,
    });
  }
  Plotly.react("histogram", traces, {
    ...LAYOUT_BASE,
    xaxis: { ...LAYOUT_BASE.xaxis, title: { text: "Power (dBm)" }, range: X_RANGE },
    yaxis: { ...LAYOUT_BASE.yaxis, title: { text: "% of readings" }, rangemode: "tozero" },
    bargap: 0, showlegend: traces.length > 1,
    legend: { orientation: "h", x: 1, xanchor: "right", y: 1.08 },
  }, CONFIG);
}

// Every calendar day of the year, with null for days without data, so the trend line shows gaps.
function yearSeries(field) {
  const out = { x: [], y: [] };
  for (let m = 1; m <= 12; m++) {
    for (let d = 1; d <= daysInMonth(m); d++) {
      const date = `${YEAR}-${pad(m)}-${pad(d)}`;
      out.x.push(date);
      out.y.push(BY_DATE[date] ? BY_DATE[date][field] : null);
    }
  }
  return out;
}

// One closed polygon per run of consecutive observed days (null-separated), so gaps stay empty.
function percentileBand(lo, hi) {
  const x = [], y = [];
  let run = [];
  const flush = () => {
    if (run.length) {
      x.push(...run.map(i => hi.x[i]), ...run.slice().reverse().map(i => lo.x[i]), null);
      y.push(...run.map(i => hi.y[i]), ...run.slice().reverse().map(i => lo.y[i]), null);
    }
    run = [];
  };
  hi.y.forEach((v, i) => (v == null ? flush() : run.push(i)));
  flush();
  return { x, y };
}

function renderTrend() {
  // Shade the selected month or quarter.
  const shapes = [];
  const span = state.quarter ? quarterMonths(state.quarter) : state.month === "all" ? null : [state.month];
  if (span) {
    const first = span[0], last = span[span.length - 1];
    shapes.push({ type: "rect", xref: "x", yref: "paper", y0: 0, y1: 1, line: { width: 0 },
      fillcolor: "rgba(204,0,0,0.07)",
      x0: `${YEAR}-${pad(first)}-01`, x1: last === 12 ? `${YEAR + 1}-01-01` : `${YEAR}-${pad(last + 1)}-01` });
  }
  const p10 = yearSeries("p10"), p90 = yearSeries("p90"), med = yearSeries("median");
  const traces = [
    { ...percentileBand(p10, p90), type: "scatter", mode: "lines", line: { width: 0 }, fill: "toself",
      fillcolor: "rgba(204,0,0,0.15)", name: "10th–90th percentile", hoverinfo: "skip" },
    { x: med.x, y: med.y, type: "scatter", mode: "lines+markers", name: "Daily median",
      line: { color: "#CC0000", width: 1.5 }, marker: { size: 4, color: "#CC0000" },
      customdata: med.x.map((_, i) => [p10.y[i], p90.y[i]]),
      hovertemplate: "%{x|%b %d}: median %{y:.1f} dBm (p10 %{customdata[0]:.1f}, p90 %{customdata[1]:.1f})<extra></extra>" },
  ];
  if (state.day) {
    const d = BY_DATE[state.day];
    traces.push({ x: [d.date], y: [d.median], type: "scatter", mode: "markers", showlegend: false, hoverinfo: "skip",
      marker: { size: 11, color: "rgba(0,0,0,0)", line: { color: "#1a1a1a", width: 2 } } });
  }
  Plotly.react("trend", traces, {
    ...LAYOUT_BASE,
    margin: { t: 10, r: 20, b: 40, l: 65 },
    xaxis: { ...LAYOUT_BASE.xaxis, type: "date", range: [`${YEAR}-01-01`, `${YEAR}-12-31`], tickformat: "%b" },
    yaxis: { ...LAYOUT_BASE.yaxis, title: { text: "dBm" } },
    shapes, legend: { orientation: "h", x: 1, xanchor: "right", y: 1.12 },
  }, CONFIG);
}

function statCells(s, approx) {
  const a = approx ? "≈" : "";
  return [fmt(s.min), fmt(s.mean, 2), a + fmt(s.median, 2), a + fmt(s.p10, 2), a + fmt(s.p90, 2), fmt(s.max), fmt(s.peak_bin_low)];
}

function renderTable() {
  const head = document.getElementById("table-head");
  const body = document.getElementById("table-body");
  const title = document.getElementById("table-title");
  const cols = ["Min", "Mean", "Median", "p10", "p90", "Max", "Peak bin"];
  body.replaceChildren();

  if (state.month === "all") {
    // Whole year or a quarter: one row per month.
    const months = state.quarter ? quarterMonths(state.quarter) : MONTHS.map((_, i) => i + 1);
    const period = state.quarter ? quarterName(state.quarter) : String(YEAR);
    title.textContent = `Monthly statistics — ${period} (click a month)`;
    head.innerHTML = `<tr><th>Month</th><th>Days</th><th>Sweeps</th>${cols.map(c => `<th>${c}</th>`).join("")}</tr>`;
    months.forEach(m => {
      const days = daysInMonths([m]);
      const tr = el("tr");
      tr.append(el("td", {}, MONTHS[m - 1]));
      if (!days.length) {
        tr.className = "missing";
        tr.append(el("td", {}, "0"), el("td", { colspan: cols.length + 1 }, "no data"));
      } else {
        const s = pooledStats(days);
        tr.onclick = () => select({ month: m });
        [`${days.length}/${daysInMonth(m)}`, s.sweeps.toLocaleString(), ...statCells(s, true)]
          .forEach(v => tr.append(el("td", {}, v)));
      }
      body.append(tr);
    });
    return;
  }

  title.textContent = `Daily statistics — ${MONTHS[state.month - 1]} ${YEAR} (click a day)`;
  head.innerHTML = `<tr><th>Date</th><th>Sweeps</th>${cols.map(c => `<th>${c}</th>`).join("")}</tr>`;
  for (let d = 1; d <= daysInMonth(state.month); d++) {
    const date = `${YEAR}-${pad(state.month)}-${pad(d)}`;
    const day = BY_DATE[date];
    const tr = el("tr");
    tr.append(el("td", {}, `${MONTHS[state.month - 1].slice(0, 3)} ${d}`));
    if (!day) {
      tr.className = "missing";
      tr.append(el("td", { colspan: cols.length + 1 }, "no data recorded"));
    } else {
      if (state.day === date) tr.className = "selected";
      tr.onclick = () => select({ month: state.month, day: date });
      [String(day.sweeps), ...statCells(day, false)].forEach(v => tr.append(el("td", {}, v)));
    }
    body.append(tr);
  }
}

function render() {
  const stats = pooledStats(selectedDays());
  renderPicker();
  renderSummary(stats);
  renderHistogram(stats);
  renderTrend();
  renderTable();
}

async function boot() {
  const root = document.body.dataset.root;
  const id = document.body.dataset.bandId;
  try {
    const res = await fetch(`${root}data/bands/${id}.json`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    DATA = await res.json();
    BY_DATE = Object.fromEntries(DATA.days.map(d => [d.date, d]));
    YEAR_STATS = pooledStats(DATA.days);
    const nz = YEAR_STATS.hist.map((n, i) => (n ? i : -1)).filter(i => i >= 0);
    X_RANGE = [BIN_LOW + BIN_W * nz[0] - 1, BIN_LOW + BIN_W * (nz[nz.length - 1] + 1) + 1];
    document.getElementById("chip-days").textContent = `${DATA.days.length} observed days`;
    state = readHash();
    render();
    document.getElementById("trend").on("plotly_click", ev => {
      const date = ev.points[0].x.slice(0, 10);
      if (BY_DATE[date]) select({ month: monthOf(date), day: date });
    });
    window.addEventListener("hashchange", () => { state = readHash(); render(); });
  } catch (err) {
    document.querySelector("main").prepend(el("p", { class: "draft-note" }, `Could not load band data: ${err.message}`));
  } finally {
    const o = document.getElementById("loading-overlay");
    o.classList.add("hidden");
    setTimeout(() => o.remove(), 400);
  }
}
boot();
