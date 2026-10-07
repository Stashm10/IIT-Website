# Daily & Monthly Band Histograms Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Static site showing every bands.json band's power histogram for every observed 2018 day, browsable by month.

**Architecture:** A Python pipeline reads the Drive `.h5` files read-only, writes one compact JSON per band (daily sparse histograms + stats). A Python generator writes static HTML pages that sum daily histograms client-side for month / year views.

**Tech Stack:** Python 3 + h5py + numpy (venv), pytest; static HTML + Plotly 2.32 (CDN, as today).

**Spec:** `docs/superpowers/specs/2026-10-06-daily-histograms-design.md`

## Global Constraints
- Drive data dir `/Users/romanstashkiv/Desktop/IIt_Project_V2/2018 IITSO Wideband Data` is opened read-only (`h5py.File(p, "r")`); never written.
- Bins: edges `-150.0 .. +20.0` step `0.5` (340 bins), from `bands.json["histogram_bins"]`.
- Band membership: `low_mhz <= f < high_mhz`, f = `np.linspace(start_freq, stop_freq, num_points)/1e6`.
- Day key = date in filename; same-date files pooled.
- Visual style matches current site (IIT red `#CC0000`, Arial, white cards).

---

### Task 1: Core stats module

**Files:**
- Create: `tools/spectrum.py`, `tools/test_spectrum.py`, `tools/requirements.txt` (`h5py`, `numpy`, `pytest`)

**Interfaces — Produces:**
- `EDGES: np.ndarray` (341 edges)
- `day_key(filename: str) -> str` — `"IITSO_20180101000307_(30-6000_MHz).h5"` → `"2018-01-01"`
- `band_stats(values: np.ndarray) -> dict` — keys `readings, sum, min, max, mean, median, p10, p90, peak_bin_low, hist` where `hist = {"o": int, "c": list[int]}` (sparse)
- `dense(hist: dict) -> np.ndarray` (length 340)
- `band_columns(freqs_mhz, low, high) -> np.ndarray` (bool mask)

- [ ] Step 1: Write tests

```python
import numpy as np
from spectrum import day_key, band_stats, dense, band_columns, EDGES

def test_day_key():
    assert day_key("IITSO_20181214080327_(30-6000_MHz).h5") == "2018-12-14"

def test_band_stats_and_sparse_roundtrip():
    v = np.array([-100.2, -100.1, -90.0, -89.9])
    s = band_stats(v)
    assert s["readings"] == 4 and s["min"] == -100.2 and s["max"] == -89.9
    d = dense(s["hist"])
    assert d.sum() == 4 and len(d) == 340
    assert d[int((-100.5 + 150) / 0.5)] == 2      # -100.2, -100.1 in [-100.5,-100.0)
    assert s["peak_bin_low"] == -100.5

def test_band_columns_half_open():
    f = np.array([44.0, 44.5, 46.6])
    assert band_columns(f, 44, 46.6).tolist() == [True, True, False]
```

- [ ] Step 2: `venv/bin/pytest tools -q` → FAIL (module missing)
- [ ] Step 3: Implement

```python
import re, numpy as np
EDGES = np.round(np.arange(-150.0, 20.0 + 0.25, 0.5), 2)
def day_key(name):
    m = re.search(r"IITSO_(\d{4})(\d{2})(\d{2})", name); return f"{m[1]}-{m[2]}-{m[3]}"
def band_columns(f, low, high): return (f >= low) & (f < high)
def band_stats(v):
    v = np.asarray(v, dtype=np.float64).ravel()
    counts, _ = np.histogram(np.clip(v, EDGES[0], EDGES[-1] - 1e-9), bins=EDGES)
    nz = np.nonzero(counts)[0]; o, e = int(nz[0]), int(nz[-1]) + 1
    p10, med, p90 = np.percentile(v, [10, 50, 90])
    r = lambda x: round(float(x), 4)
    return {"readings": int(v.size), "sum": float(v.sum()), "min": r(v.min()), "max": r(v.max()),
            "mean": r(v.mean()), "median": r(med), "p10": r(p10), "p90": r(p90),
            "peak_bin_low": float(EDGES[int(counts.argmax())]),
            "hist": {"o": o, "c": counts[o:e].tolist()}}
def dense(h):
    d = np.zeros(len(EDGES) - 1, dtype=np.int64); d[h["o"]:h["o"] + len(h["c"])] = h["c"]; return d
```

- [ ] Step 4: tests PASS
- [ ] Step 5: Commit `feat: core spectrum stats module`

### Task 2: Day processor + reference validation gate

**Files:**
- Create: `tools/build_data.py`, `tools/test_reference.py`

**Interfaces:**
- Consumes: Task 1 functions.
- Produces: `process_day(paths: list[str], bands: list[dict]) -> dict` → `{"date", "files", "sweeps", "bands": {band_id: band_stats(...) + {"num_points"}}}`; CLI `build_data.py [--only 2018-01-01] [--workers N]` writing `tools/cache/<date>.json` (skips existing), then assembling `data/bands/<id>.json` and `data/index.json`.

- [ ] Step 1: Test — run `process_day` on the Jan 1 file and compare every band to `reference_2018-01-01.json`: `num_points`, `num_readings`, `peak_bin_low_dbm` equal; `min/max/mean/median/p10/p90` within 0.01 dB.

```python
import json, glob
from build_data import process_day, load_bands, DATA_DIR, V2
def test_jan1_matches_reference():
    ref = json.load(open(V2 + "/reference_2018-01-01.json"))
    bands = load_bands()
    day = process_day(glob.glob(DATA_DIR + "/IITSO_20180101*.h5"), bands)
    for rb in ref["bands"]:
        got = day["bands"][rb["id"]]
        assert got["num_points"] == rb["num_points"] and got["readings"] == rb["num_readings"]
        assert got["peak_bin_low"] == rb["peak_bin_low_dbm"], rb["id"]
        for k in ["min", "max", "mean", "median", "p10", "p90"]:
            assert abs(got[k] - rb[k + "_dbm"]) < 0.01, (rb["id"], k)
```

- [ ] Step 2: FAIL (no module)
- [ ] Step 3: Implement `process_day`: for each path open read-only; per needed sub-band index read `powers[:]`, `start_time`, attrs → freqs; concatenate same-date rows across files; per band slice `powers[:, mask]` → `band_stats` + `num_points = mask.sum()`. `sweeps` = rows of sub-band 0.
- [ ] Step 4: PASS → this is the gate before the full run.
- [ ] Step 5: Commit `feat: daily band processor validated against reference`

### Task 3: Full-year run (background) + assembly

- [ ] Step 1: `venv/bin/python tools/build_data.py --workers 4` in background; resumable via cache.
- [ ] Step 2: Assemble → `data/index.json` (`groups`, `bands` meta, `dates`, `status`) and `data/bands/<id>.json` (`band` meta, `days: [{date, sweeps, files, ...band_stats, num_points}]`).
- [ ] Step 3: Sanity: 310 dates (315 files − 5 duplicate dates), every band has every date, total size < 40 MB.
- [ ] Step 4: Commit data.

### Task 4: Site generator

**Files:**
- Create: `tools/build_site.py`, `tools/templates/index.html`, `tools/templates/band.html`, `assets/band.js`, `assets/site.css`
- Modify: `index.html` (generated; header/nav markup reused from the existing file)
- Delete: `square/`, old `data/*.json`, `data/square/`

- `index.html`: existing header kept verbatim; banner "Spectrum Observatory — 44–900 MHz · 2018"; draft notice; 9 group cards, each a flex bar of band buttons (`flex: high-low`, category colour, tooltip with name + range), plus a legend of categories and a list view (name, range) for narrow bands.
- `band/<id>/index.html`: back link, meta chips, month tabs + "All 2018", day buttons (disabled when no data), stat cards, Plotly bar chart (% of readings vs dBm, x range trimmed to nonzero bins of the whole year), daily stats table grouped by month with selected row highlighted. `assets/band.js` holds: `sumHist(days)`, `pooledStats(days, hist)` (exact mean/min/max; median/p10/p90 from cumulative histogram at bin midpoints), `render(selection)`.
- [ ] Unit check of `pooledStats` logic via a quick node run if available, else browser console.
- [ ] Commit `feat: static site for daily/monthly band histograms`

### Task 5: Browser verification
- [ ] Serve repo root with `python3 -m http.server`; check index, a 700–800 band (B14 `700-800--758-760`), Feb (missing days), "All 2018", mobile width. No console errors.
- [ ] Commit fixes; report to user. Do not push.
