"""Build per-band daily histograms for 2018 from the IITSO wideband .h5 files.

The source files are opened read-only and never modified.

    python tools/build_data.py                    # process every day, then assemble
    python tools/build_data.py --only 2018-01-01  # process one day
    python tools/build_data.py --assemble-only    # rebuild data/ from tools/cache/

Each day is cached in tools/cache/<date>.json, so an interrupted run resumes.
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import h5py
import numpy as np

from spectrum import band_columns, band_stats, day_key

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
V2_DIR = os.environ.get("IIT_V2_DIR", "/Users/romanstashkiv/Desktop/IIt_Project_V2")
DATA_DIR = os.environ.get("IIT_DATA_DIR", os.path.join(V2_DIR, "2018 IITSO Wideband Data"))
CACHE_DIR = os.path.join(HERE, "cache")
OUT_DIR = os.path.join(REPO, "data")


def load_band_plan():
    with open(os.path.join(V2_DIR, "bands.json")) as fh:
        return json.load(fh)


def load_bands():
    """Flat list of every band in bands.json, each tagged with its group id."""
    bands = []
    for group in load_band_plan()["groups"]:
        for band in group["bands"]:
            bands.append({**band, "group_id": group["id"]})
    return bands


def files_by_day():
    days = defaultdict(list)
    for name in sorted(os.listdir(DATA_DIR)):
        if name.startswith("IITSO_") and name.endswith(".h5"):
            days[day_key(name)].append(os.path.join(DATA_DIR, name))
    return dict(sorted(days.items()))


def read_subband(f, idx):
    ds = f["sessions/0/spectrum"][str(idx)]
    freqs = np.linspace(float(ds.attrs["start_freq"]), float(ds.attrs["stop_freq"]),
                        int(ds.attrs["num_points"])) / 1e6
    return freqs, ds["powers"][:]


def process_day(paths, bands):
    """Stats for every band over all sweeps of all files belonging to one day."""
    needed = sorted({b["subband"]["index_in_reference_file"] for b in bands})
    freqs, chunks = {}, defaultdict(list)
    for path in paths:
        with h5py.File(path, "r") as f:  # read-only: source data is never altered
            for idx in needed:
                fr, powers = read_subband(f, idx)
                if idx in freqs and not np.allclose(freqs[idx], fr):
                    raise ValueError(f"sub-band {idx} frequency grid differs in {path}")
                freqs[idx] = fr
                chunks[idx].append(powers)
    powers = {idx: np.concatenate(chunks[idx], axis=0) for idx in needed}

    out = {}
    for band in bands:
        idx = band["subband"]["index_in_reference_file"]
        mask = band_columns(freqs[idx], band["low_mhz"], band["high_mhz"])
        stats = band_stats(powers[idx][:, mask])
        stats["num_points"] = int(mask.sum())
        stats["sweeps"] = int(powers[idx].shape[0])
        out[band["id"]] = stats
    return {
        "date": day_key(os.path.basename(paths[0])),
        "files": [os.path.basename(p) for p in paths],
        "sweeps": int(powers[needed[0]].shape[0]),
        "bands": out,
    }


def _cache_path(date):
    return os.path.join(CACHE_DIR, f"{date}.json")


def _work(item):
    date, paths = item
    t0 = time.time()
    try:
        day = process_day(paths, load_bands())
    except Exception as exc:  # a bad file must not stop the year
        return date, f"ERROR {exc!r}"
    tmp = _cache_path(date) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(day, fh, separators=(",", ":"))
    os.replace(tmp, _cache_path(date))
    return date, f"ok {day['sweeps']} sweeps, {time.time() - t0:.0f}s"


def assemble():
    """Combine cached days into data/index.json and data/bands/<band_id>.json."""
    plan = load_band_plan()
    bands = load_bands()
    days = []
    for name in sorted(os.listdir(CACHE_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(CACHE_DIR, name)) as fh:
                days.append(json.load(fh))

    os.makedirs(os.path.join(OUT_DIR, "bands"), exist_ok=True)
    for band in bands:
        rows = []
        for day in days:
            s = dict(day["bands"][band["id"]])
            s["sum"] = round(s["sum"], 2)
            rows.append({"date": day["date"], "files": day["files"], **s})
        with open(os.path.join(OUT_DIR, "bands", f"{band['id']}.json"), "w") as fh:
            json.dump({"band": band, "days": rows}, fh, separators=(",", ":"))

    index = {
        "version": plan["version"],
        "status": plan["status"],
        "histogram_bins": plan["histogram_bins"],
        "categories": plan["rules"]["categories"],
        "groups": [{k: v for k, v in g.items() if k != "bands"} | {"band_ids": [b["id"] for b in g["bands"]]}
                   for g in plan["groups"]],
        "bands": {b["id"]: b for b in bands},
        "dates": [d["date"] for d in days],
        "sweeps": {d["date"]: d["sweeps"] for d in days},
        # Days whose files exist but could not be read (e.g. corrupt HDF5 header).
        "unreadable": {date: [os.path.basename(p) for p in paths]
                       for date, paths in files_by_day().items()
                       if date not in {d["date"] for d in days}},
    }
    with open(os.path.join(OUT_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, separators=(",", ":"))
    print(f"assembled {len(days)} days x {len(bands)} bands into {OUT_DIR}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="process a single YYYY-MM-DD")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--assemble-only", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not args.assemble_only:
        todo = [(d, p) for d, p in files_by_day().items()
                if (args.only is None or d == args.only) and not os.path.exists(_cache_path(d))]
        print(f"{len(todo)} day(s) to process", flush=True)
        failures = 0
        with Pool(args.workers) as pool:
            for n, (date, msg) in enumerate(pool.imap_unordered(_work, todo), 1):
                failures += msg.startswith("ERROR")
                print(f"[{n}/{len(todo)}] {date} {msg}", flush=True)
        if failures:
            print(f"{failures} day(s) failed; re-run to retry them", file=sys.stderr)
    if args.only is None:
        assemble()


if __name__ == "__main__":
    main()
