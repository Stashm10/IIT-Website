"""Record the receiver settings behind every observed day and when they change.

For every source file that contributed to a day (the `files` lists in tools/cache/<date>.json),
this opens the file read-only and reads only HDF5 attributes and the small start_time /
sweep_time datasets. The power data is never read and the per-day cache is not touched.

    python tools/build_settings.py --data-dir PATH     # writes data/settings.json

The data folder can also be given with the IIT_DATA_DIR environment variable.
"""
import argparse
import json
import os
from collections import defaultdict
from multiprocessing import Pool

import h5py
import numpy as np

from build_data import CACHE_DIR, OUT_DIR, load_bands, resolve_data_dir

# Sub-band attributes that define how the receiver was set.
FIELDS = ["start_freq", "stop_freq", "num_points", "rbw", "vbw", "atten", "ref_level", "avg_len", "name"]
# File- and session-level groups whose attributes are also tracked through the year.
GROUPS = ["/", "/sessions", "/sessions/0", "/sessions/0/spectrum"]


def plain(value):
    """numpy / bytes attribute values -> plain JSON-friendly Python values."""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def mhz_key(start_mhz, stop_mhz):
    """'30-54' style key for a sub-band frequency range."""
    def f(x):
        text = str(float(x))
        return text.rstrip("0").rstrip(".")
    return f"{f(start_mhz)}-{f(stop_mhz)}"


def read_file(path, indices):
    """Attributes and sweep timing of one file. Never reads the `powers` dataset."""
    with h5py.File(path, "r") as f:  # read-only: source data is never altered
        groups = {g: {k: plain(v) for k, v in f[g].attrs.items()} for g in GROUPS if g in f}
        subbands = {}
        for idx in indices:
            g = f["sessions/0/spectrum"][str(idx)]
            settings = {k: plain(g.attrs[k]) if k in g.attrs else None for k in FIELDS}
            settings.update({k: plain(v) for k, v in g.attrs.items() if k not in FIELDS})
            starts = g["start_time"][:]
            sweep_times = g["sweep_time"][:] if "sweep_time" in g else np.array([])
            subbands[idx] = {
                "settings": settings,
                "sweeps": int(len(starts)),
                "interval_s": float(np.median(np.diff(starts))) if len(starts) > 1 else None,
                "sweep_time_s": float(np.median(sweep_times)) if len(sweep_times) else None,
            }
    return {"groups": groups, "subbands": subbands}


def freq_step_khz(settings):
    if settings.get("num_points", 0) and settings["num_points"] > 1:
        return round((settings["stop_freq"] - settings["start_freq"]) / (settings["num_points"] - 1) / 1e3, 4)
    return None


def summarize_subband(days):
    """days: [(date, [(file, info), ...]), ...] sorted by date, info as from read_file()['subbands'][i].
    Returns periods of identical settings, the changes between them, and days whose files disagree."""
    periods, changes, mixed = [], [], []
    prev_date, prev = None, None
    for date, files in days:
        distinct = {json.dumps(info["settings"], sort_keys=True) for _, info in files}
        if len(distinct) > 1:
            mixed.append({"date": date, "files": {name: info["settings"] for name, info in files}})
        # A day's settings: those of its file with the most sweeps (identical unless the day is mixed).
        settings = max(files, key=lambda fi: fi[1]["sweeps"])[1]["settings"]
        if prev is None or settings != prev:
            if prev is not None:
                for field in sorted(set(prev) | set(settings)):
                    if prev.get(field) != settings.get(field):
                        changes.append({"date": date, "previous_date": prev_date, "field": field,
                                        "old": prev.get(field), "new": settings.get(field)})
            periods.append({"from": date, "to": date, "days": 0, "settings": settings,
                            "freq_step_khz": freq_step_khz(settings)})
        periods[-1]["to"] = date
        periods[-1]["days"] += 1
        prev_date, prev = date, settings
    return {"periods": periods, "changes": changes, "mixed_days": mixed}


def varying_attributes(file_groups):
    """file_groups: [(date, file, {group_path: {attr: value}}), ...] sorted by date.
    Returns every group-level attribute whose value changes during the year."""
    names = sorted({(path, attr) for _, _, groups in file_groups
                    for path, attrs in groups.items() for attr in attrs})
    out = []
    for path, attr in names:
        # A missing attribute counts as the value None, so appearing or disappearing is a change too.
        values = [(d, n, groups.get(path, {}).get(attr)) for d, n, groups in file_groups]
        changes = [{"date": d, "file": n, "old": values[i - 1][2], "new": v}
                   for i, (d, n, v) in enumerate(values) if i and v != values[i - 1][2]]
        if changes:
            out.append({"path": path, "name": attr, "changes": changes})
    return out


def _read(job):
    date, path, indices = job
    return date, os.path.basename(path), read_file(path, indices)


def build(data_dir, workers=6):
    bands = load_bands()
    keys = {}  # sub-band index -> '30-54'
    for b in bands:
        sb = b["subband"]
        keys[sb["index_in_reference_file"]] = mhz_key(sb["start_mhz"], sb["stop_mhz"])
    indices = sorted(keys)

    jobs = []
    for name in sorted(os.listdir(CACHE_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(CACHE_DIR, name)) as fh:
                day = json.load(fh)
            jobs += [(day["date"], os.path.join(data_dir, f), indices) for f in day["files"]]
    with Pool(workers) as pool:
        results = sorted(pool.map(_read, jobs), key=lambda r: (r[0], r[1]))

    by_day = defaultdict(lambda: defaultdict(list))
    for date, name, info in results:
        for idx in indices:
            by_day[idx][date].append((name, info["subbands"][idx]))

    subbands, all_intervals = {}, []
    for idx in indices:
        days = sorted(by_day[idx].items())
        intervals = [i["interval_s"] for _, files in days for _, i in files if i["interval_s"]]
        sweep_times = [i["sweep_time_s"] for _, files in days for _, i in files if i["sweep_time_s"]]
        all_intervals += intervals
        subbands[keys[idx]] = {
            "index": idx,
            "typical_sweep_interval_s": round(float(np.median(intervals)), 1),
            "typical_sweep_time_s": round(float(np.median(sweep_times)), 2) if sweep_times else None,
            **summarize_subband(days),
        }

    return {
        "description": ("Receiver settings of every observed day, read from HDF5 attributes only "
                        "(power data not read). A period is a run of consecutive observed dates with "
                        "identical settings; a change is dated by the first day with the new value."),
        "fields": FIELDS,
        "files_read": len(results),
        "typical_sweep_interval_s": round(float(np.median(all_intervals)), 1),
        "subbands": subbands,
        "varying_attributes": varying_attributes([(d, n, info["groups"]) for d, n, info in results]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", help="folder of 2018 .h5 files (default: $IIT_DATA_DIR)")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    settings = build(resolve_data_dir(args.data_dir), args.workers)
    out = os.path.join(OUT_DIR, "settings.json")
    with open(out, "w") as fh:
        json.dump(settings, fh, indent=1)
    n_changes = sum(len(s["changes"]) for s in settings["subbands"].values())
    print(f"read {settings['files_read']} files; {n_changes} setting change(s); wrote {out}")


if __name__ == "__main__":
    main()
