import os
import json
import numpy as np
import h5py
from flask import Flask, jsonify, render_template, abort
from datetime import datetime
import pytz

app = Flask(__name__)

HDF5_PATH = os.environ.get(
    "IIT_HDF5_PATH",
    os.path.join(os.path.dirname(__file__), "..", "IITSO_20180101000307_(30-6000_MHz).h5 copy"),
)
FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))

# 19 allocation squares for 30–54 MHz
ALLOCATIONS = [
    {"id": "mobile_30.0_30.56",           "name": "Mobile",               "low": 30.0,  "high": 30.56},
    {"id": "land_mobile_30.56_32.0",       "name": "Land Mobile",          "low": 30.56, "high": 32.0},
    {"id": "mobile_32.0_33.0",             "name": "Mobile",               "low": 32.0,  "high": 33.0},
    {"id": "land_mobile_33.0_34.0",        "name": "Land Mobile",          "low": 33.0,  "high": 34.0},
    {"id": "mobile_34.0_35.0",             "name": "Mobile",               "low": 34.0,  "high": 35.0},
    {"id": "land_mobile_35.0_36.0",        "name": "Land Mobile",          "low": 35.0,  "high": 36.0},
    {"id": "mobile_36.0_37.0",             "name": "Mobile",               "low": 36.0,  "high": 37.0},
    {"id": "land_mobile_fixed_37.0_37.5",  "name": "Land Mobile / Fixed",  "low": 37.0,  "high": 37.5},
    {"id": "fixed_37.5_38.0",             "name": "Fixed",                "low": 37.5,  "high": 38.0},
    {"id": "radio_astronomy_38.0_38.25",   "name": "Radio Astronomy",      "low": 38.0,  "high": 38.25},
    {"id": "land_mobile_38.25_39.0",       "name": "Land Mobile / Mobile", "low": 38.25, "high": 39.0},
    {"id": "land_mobile_39.0_40.0",        "name": "Land Mobile",          "low": 39.0,  "high": 40.0},
    {"id": "mobile_40.0_42.0",             "name": "Mobile",               "low": 40.0,  "high": 42.0},
    {"id": "land_mobile_42.0_43.69",       "name": "Land Mobile",          "low": 42.0,  "high": 43.69},
    {"id": "mobile_43.69_46.6",            "name": "Mobile",               "low": 43.69, "high": 46.6},
    {"id": "land_mobile_46.6_47.0",        "name": "Land Mobile",          "low": 46.6,  "high": 47.0},
    {"id": "mobile_47.0_49.6",             "name": "Mobile",               "low": 47.0,  "high": 49.6},
    {"id": "mobile_49.6_50.0",             "name": "Mobile",               "low": 49.6,  "high": 50.0},
    {"id": "amateur_50.0_54.0",            "name": "Amateur",              "low": 50.0,  "high": 54.0},
]

ALLOC_BY_ID = {a["id"]: a for a in ALLOCATIONS}

_data = {}


def compute_histogram(flat):
    bin_min = float(np.floor(flat.min() / 0.5) * 0.5)
    bin_max = float(np.ceil(flat.max() / 0.5) * 0.5)
    bins = np.arange(bin_min, bin_max + 0.5, 0.5)
    counts, edges = np.histogram(flat, bins=bins)
    return edges.tolist(), counts.tolist()


def compute_stats(flat):
    noise_floor = float(np.percentile(flat, 10))
    occupancy = float(np.mean(flat > noise_floor + 6.0) * 100)
    return {
        "min_power": float(flat.min()),
        "max_power": float(flat.max()),
        "mean_power": float(flat.mean()),
        "noise_floor": noise_floor,
        "occupancy_pct": round(occupancy, 2),
    }


def load_data():
    try:
        with h5py.File(HDF5_PATH, "r") as f:
            sb = f["sessions/0/spectrum/0"]
            powers = sb["powers"][:]
            start_time = sb["start_time"][:]

        freqs = np.linspace(30.0, 54.0, 8001)
        chicago = pytz.timezone("America/Chicago")
        timestamps = [
            datetime.fromtimestamp(float(t), tz=chicago).strftime("%H:%M:%S")
            for t in start_time
        ]

        _data["powers"] = powers
        _data["freqs"] = freqs
        _data["timestamps"] = timestamps

        # Precompute per-square slices
        squares = {}
        for alloc in ALLOCATIONS:
            idx = np.where((freqs >= alloc["low"]) & (freqs < alloc["high"]))[0]
            if len(idx) == 0:
                idx = np.where((freqs >= alloc["low"]) & (freqs <= alloc["high"]))[0]
            sub_powers = powers[:, idx]
            sub_freqs = freqs[idx]
            squares[alloc["id"]] = {
                "powers": sub_powers,
                "freqs": sub_freqs,
                "num_cols": len(idx),
            }
        _data["squares"] = squares
        print(f"[OK] Loaded HDF5: powers={powers.shape}, squares={len(squares)}")
    except Exception as e:
        print(f"[ERROR] Failed to load HDF5: {e}")
        _data["error"] = str(e)


load_data()


# ── Main page ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "error" in _data:
        return f"<h1>Error loading data</h1><pre>{_data['error']}</pre>", 500
    return render_template("index.html", allocations=ALLOCATIONS)


# ── Per-square page ──────────────────────────────────────────────────────────
@app.route("/square/<square_id>")
def square_page(square_id):
    if square_id not in ALLOC_BY_ID:
        abort(404)
    alloc = ALLOC_BY_ID[square_id]
    return render_template("square.html", alloc=alloc)


# ── Full-band data endpoints ──────────────────────────────────────────────────
@app.route("/api/data")
def api_data():
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    powers = _data["powers"]
    freqs = _data["freqs"]
    return jsonify({
        "freqs": freqs[::10].tolist(),
        "timestamps": _data["timestamps"],
        "powers": powers[:, ::10].tolist(),
    })


@app.route("/api/histogram")
def api_histogram():
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    edges, counts = compute_histogram(_data["powers"].flatten())
    return jsonify({"edges": edges, "counts": counts})


@app.route("/api/stats")
def api_stats():
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    flat = _data["powers"].flatten()
    stats = compute_stats(flat)
    stats.update({
        "freq_min_mhz": 30.0,
        "freq_max_mhz": 54.0,
        "num_sweeps": int(_data["powers"].shape[0]),
    })
    return jsonify(stats)


# ── Per-square data endpoints ─────────────────────────────────────────────────
@app.route("/api/square/<square_id>")
def api_square(square_id):
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    if square_id not in _data["squares"]:
        abort(404)
    sq = _data["squares"][square_id]
    alloc = ALLOC_BY_ID[square_id]
    return jsonify({
        "id": square_id,
        "name": alloc["name"],
        "low": alloc["low"],
        "high": alloc["high"],
        "freqs": sq["freqs"].tolist(),
        "timestamps": _data["timestamps"],
        "powers": sq["powers"].tolist(),
        "num_cols": sq["num_cols"],
    })


@app.route("/api/square/<square_id>/histogram")
def api_square_histogram(square_id):
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    if square_id not in _data["squares"]:
        abort(404)
    flat = _data["squares"][square_id]["powers"].flatten()
    edges, counts = compute_histogram(flat)
    return jsonify({"edges": edges, "counts": counts})


@app.route("/api/square/<square_id>/stats")
def api_square_stats(square_id):
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    if square_id not in _data["squares"]:
        abort(404)
    sq = _data["squares"][square_id]
    alloc = ALLOC_BY_ID[square_id]
    flat = sq["powers"].flatten()
    stats = compute_stats(flat)
    stats.update({
        "freq_min_mhz": alloc["low"],
        "freq_max_mhz": alloc["high"],
        "num_sweeps": int(sq["powers"].shape[0]),
        "num_cols": sq["num_cols"],
    })
    return jsonify(stats)


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
