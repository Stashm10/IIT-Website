# Daily & Monthly Band Histograms — Design

Date: 2026-10-06 · Branch: `daily-histograms`

## Goal
Replace the single-day (Jan 1 2018), 30–54 MHz site with one that shows the power
distribution of every band in `bands.json` (9 poster groups, 91 bands, 44–900 MHz)
for every observed day of 2018, browsable by month.

## Inputs (read-only)
- `IIt_Project_V2/2018 IITSO Wideband Data/*.h5` — 315 daily files on Google Drive.
  Opened with `h5py.File(path, "r")` only. Nothing is ever written there.
- `IIt_Project_V2/bands.json` — band plan + fixed histogram bins (-150..+20 dBm, 0.5 dB, 340 bins).
- `IIt_Project_V2/reference_2018-01-01.json` — expected per-band stats for the Jan 1 file.

## Data pipeline (`tools/build_data.py`)
1. **Day key** = `YYYY-MM-DD` taken from the filename (`IITSO_YYYYMMDDhhmmss_...`). Each
   file starts at ~00:00 Chicago time. Two files with the same date are pooled into one day.
2. **Band slice**: sub-band `bands[i].subband.index_in_reference_file` → `sessions/0/spectrum/<idx>`;
   frequencies `np.linspace(start_freq, stop_freq, num_points)` in MHz; points where
   `low_mhz <= f < high_mhz`; all sweeps.
3. **Per day, per band** store: sweep count, reading count, sum (for exact pooled mean),
   min, max, mean, median, p10, p90 (`np.percentile`, default linear), and histogram counts on
   the fixed bins, stored sparse as `{o: first-nonzero-bin, c: [counts...]}`.
4. **Cache**: one JSON per source file in `tools/cache/` so an interrupted run resumes.
5. **Assemble**: `data/bands/<band_id>.json` = band metadata + list of days sorted by date.
   `data/index.json` = groups, bands, list of observed dates.
6. **Validation gate**: Jan 1 results must match `reference_2018-01-01.json` for all 91 bands
   (num_points, num_readings, peak bin exactly; dBm stats within 0.01 dB) before the full run.

## Aggregation (client side)
Month / "All 2018" histogram = element-wise sum of daily counts (exact). Pooled mean =
Σsum / Σreadings (exact). Pooled min/max exact. Pooled median/p10/p90 read off the summed
histogram (bin-resolution, ±0.5 dB; labelled as such). Histogram plotted as % of readings.

## Site (`tools/build_site.py` generates static HTML)
- `index.html`: existing IIT header/branding kept; 30–54 MHz chart replaced with 9 group
  sections, each a proportional bar of its bands coloured by category, linking to band pages.
  "Draft band plan" notice (bands.json status is DRAFT).
- `band/<band_id>/index.html`: month tabs (Jan–Dec + All 2018), day buttons for the selected
  month (missing days disabled), Plotly histogram, stat cards for the selection, daily stats
  table grouped by month, band services / notes / sub-band receiver settings.
- Old `square/` and `data/` (30–54 MHz, Jan 1) removed; preserved in git history.

## Testing
- `tools/test_pipeline.py`: date-key parsing & pooling, sparse histogram round-trip and summing,
  Jan 1 vs reference file.
- Browser check of index and several band pages (incl. a month with missing days).

## Out of scope
Raw sweep matrices; anomaly/episode detection from the poster; pushing to GitHub (only on request).
