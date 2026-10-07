"""Build per-band daily histograms for 2018 from the IITSO wideband .h5 files.

The source files are opened read-only and never modified.

    python tools/build_data.py --data-dir PATH                    # process every day, then assemble
    python tools/build_data.py --data-dir PATH --only 2018-01-01  # process one day
    python tools/build_data.py --data-dir PATH --assemble-only    # rebuild data/ from tools/cache/

The data folder can also be given with the IIT_DATA_DIR environment variable.
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
# bands.json and reference_2018-01-01.json live next to this script; IIT_V2_DIR overrides that.
PLAN_DIR = os.environ.get("IIT_V2_DIR", HERE)
# Folder of 2018 .h5 files: from --data-dir or IIT_DATA_DIR (no default).
DATA_DIR = os.environ.get("IIT_DATA_DIR")
NO_DATA_DIR = "No data folder given: pass --data-dir PATH or set IIT_DATA_DIR=PATH (the folder of 2018 .h5 files)."
CACHE_DIR = os.path.join(HERE, "cache")
OUT_DIR = os.path.join(REPO, "data")


def load_band_plan():
    with open(os.path.join(PLAN_DIR, "bands.json")) as fh:
        return json.load(fh)


def load_bands():
    """Flat list of every band in bands.json, each tagged with its group id."""
    bands = []
    for group in load_band_plan()["groups"]:
        for band in group["bands"]:
            bands.append({**band, "group_id": group["id"]})
    return bands


def resolve_data_dir(arg=None):
    """The .h5 folder from --data-dir or IIT_DATA_DIR; exits with a one-line hint if neither is set."""
    data_dir = arg or DATA_DIR
    if not data_dir:
        sys.exit(NO_DATA_DIR)
    if not os.path.isdir(data_dir):
        sys.exit(f"Data folder not found: {data_dir}")
    return data_dir


def files_by_day(data_dir=None):
    """Map 'YYYY-MM-DD' -> source file paths. Several recordings on one date are pooled;
    duplicate copies of the same recording (e.g. 'name (1).h5') are counted once."""
    data_dir = data_dir or resolve_data_dir()
    recordings = {}
    for name in sorted(os.listdir(data_dir)):
        if name.startswith("IITSO_") and name.endswith(".h5"):
            stamp = name[:len("IITSO_YYYYMMDDhhmmss")]
            # sorted() puts 'name.h5' after 'name (1).h5'; keep the plain name when both exist.
            if stamp not in recordings or " (" in os.path.basename(recordings[stamp]):
                recordings[stamp] = os.path.join(data_dir, name)
    days = defaultdict(list)
    for stamp in sorted(recordings):
        days[day_key(stamp)].append(recordings[stamp])
    return dict(sorted(days.items()))


def read_subband(f, idx):
    ds = f["sessions/0/spectrum"][str(idx)]
    freqs = np.linspace(float(ds.attrs["start_freq"]), float(ds.attrs["stop_freq"]),
                        int(ds.attrs["num_points"])) / 1e6
    return freqs, ds["powers"][:]


def read_file(path, needed):
    """{sub-band index: (freqs, powers)} for one file; raises if it is unreadable or incomplete."""
    with h5py.File(path, "r") as f:  # read-only: source data is never altered
        return {idx: read_subband(f, idx) for idx in needed}


def process_day(paths, bands):
    """Stats for every band over all sweeps of all usable files belonging to one day.
    Files that cannot be opened or lack a needed sub-band are skipped and reported."""
    needed = sorted({b["subband"]["index_in_reference_file"] for b in bands})
    freqs, chunks, used, skipped = {}, defaultdict(list), [], []
    for path in paths:
        name = os.path.basename(path)
        try:
            data = read_file(path, needed)
            for idx, (fr, _) in data.items():
                if idx in freqs and not np.allclose(freqs[idx], fr):
                    raise ValueError(f"sub-band {idx} frequency grid differs")
        except (OSError, KeyError, ValueError) as exc:
            skipped.append({"file": name, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        for idx, (fr, powers) in data.items():
            freqs[idx] = fr
            chunks[idx].append(powers)
        used.append(name)
    if not used:
        raise ValueError(f"no usable file for {day_key(os.path.basename(paths[0]))}: {skipped}")
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
        "date": day_key(used[0]),
        "files": used,
        "skipped": skipped,
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


def unreadable_files(days, data_dir):
    done = {d["date"]: d for d in days}
    out = {}
    for date, paths in files_by_day(data_dir).items():
        if date in done:
            names = [s["file"] for s in done[date].get("skipped", [])]
        else:
            names = [os.path.basename(p) for p in paths]
        if names:
            out[date] = names
    return out


def assemble(data_dir):
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
        # Source files that exist but could not be used (e.g. corrupt HDF5 header).
        "unreadable": unreadable_files(days, data_dir),
    }
    with open(os.path.join(OUT_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, separators=(",", ":"))
    print(f"assembled {len(days)} days x {len(bands)} bands into {OUT_DIR}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", help="folder of 2018 .h5 files (default: $IIT_DATA_DIR)")
    ap.add_argument("--only", help="process a single YYYY-MM-DD")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--assemble-only", action="store_true")
    args = ap.parse_args()
    data_dir = resolve_data_dir(args.data_dir)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not args.assemble_only:
        todo = [(d, p) for d, p in files_by_day(data_dir).items()
                if (args.only is None or d == args.only) and not os.path.exists(_cache_path(d))]
        print(f"{len(todo)} day(s) to process", flush=True)
        failures = 0
        with Pool(args.workers) as pool:
            for n, (date, msg) in enumerate(pool.imap_unordered(_work, todo), 1):
                failures += msg.startswith("ERROR")
                print(f"[{n}/{len(todo)}] {date} {msg}", flush=True)
        if failures:
            print(f"{failures} day(s) failed; re-run to retry them (damaged source files will fail again)", file=sys.stderr)
    if args.only is None:
        assemble(data_dir)


if __name__ == "__main__":
    main()
