import os
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

_C = {
    "mobile":    "#e9d2e5",
    "lm":        "#00a1b1",
    "fixed":     "#e0088c",
    "ra":        "#ffe600",
    "amateur":   "#009370",
    "lm_mobile": "#7db8bf",
}

ALLOCATIONS = [
    {"id": "mobile_30.0_30.56",          "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 30.0,  "high": 30.56},
    {"id": "land_mobile_30.56_32.0",     "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 30.56, "high": 32.0},
    {"id": "mobile_32.0_33.0",           "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 32.0,  "high": 33.0},
    {"id": "land_mobile_33.0_34.0",      "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 33.0,  "high": 34.0},
    {"id": "mobile_34.0_35.0",           "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 34.0,  "high": 35.0},
    {"id": "land_mobile_35.0_36.0",      "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 35.0,  "high": 36.0},
    {"id": "mobile_36.0_37.0",           "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 36.0,  "high": 37.0},
    {"id": "land_mobile_fixed_37.0_37.5","top": "Land Mobile",     "top_color": _C["lm"],     "bottom": None,         "bottom_color": None,         "low": 37.0,  "high": 37.5},
    {"id": "fixed_37.5_38.0",            "top": "Radio Astronomy", "top_color": _C["ra"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 37.5,  "high": 38.0},
    {"id": "radio_astronomy_38.0_38.25", "top": "Radio Astronomy", "top_color": _C["ra"],     "middle": "Mobile",     "middle_color": _C["mobile"], "bottom": "Fixed", "bottom_color": _C["fixed"], "low": 38.0, "high": 38.25},
    {"id": "land_mobile_38.25_39.0",     "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 38.25, "high": 39.0},
    {"id": "land_mobile_39.0_40.0",      "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": None,         "bottom_color": None,         "low": 39.0,  "high": 40.0},
    {"id": "mobile_40.0_42.0",           "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Mobile",     "bottom_color": _C["mobile"], "low": 40.0,  "high": 42.0},
    {"id": "land_mobile_42.0_43.69",     "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 42.0,  "high": 43.69},
    {"id": "mobile_43.69_46.6",          "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": None,         "bottom_color": None,         "low": 43.69, "high": 46.6,  "width_pct": 7.04},
    {"id": "land_mobile_46.6_47.0",      "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 46.6,  "high": 47.0},
    {"id": "mobile_47.0_49.6",           "top": "Land Mobile",     "top_color": _C["lm"],     "bottom": None,         "bottom_color": None,         "low": 47.0,  "high": 49.6,  "width_pct": 7.04},
    {"id": "mobile_49.6_50.0",           "top": "Mobile",          "top_color": _C["mobile"], "bottom": "Fixed",      "bottom_color": _C["fixed"],  "low": 49.6,  "high": 50.0},
    {"id": "amateur_50.0_54.0",          "top": "Amateur",         "top_color": _C["amateur"],"bottom": None,         "bottom_color": None,         "low": 50.0,  "high": 54.0},
]

for _a in ALLOCATIONS:
    if _a.get("bottom") is None:
        _a["name"] = _a["top"]
    elif _a.get("middle"):
        _a["name"] = f"{_a['top']} / {_a['middle']} / {_a['bottom']}"
    else:
        _a["name"] = f"{_a['top']} / {_a['bottom']}"
    _a.setdefault("middle", None)
    _a.setdefault("middle_color", None)
    _a.setdefault("width_pct", None)

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

        squares = {}
        for alloc in ALLOCATIONS:
            idx = np.where((freqs >= alloc["low"]) & (freqs < alloc["high"]))[0]
            if len(idx) == 0:
                idx = np.where((freqs >= alloc["low"]) & (freqs <= alloc["high"]))[0]
            sub_powers = powers[:, idx]
            sub_freqs = freqs[idx]
            squares[alloc["id"]] = {"powers": sub_powers, "freqs": sub_freqs, "num_cols": len(idx)}
        _data["squares"] = squares
        print(f"[OK] Loaded HDF5: powers={powers.shape}, squares={len(squares)}")
    except Exception as e:
        print(f"[ERROR] Failed to load HDF5: {e}")
        _data["error"] = str(e)


load_data()


@app.route("/")
def index():
    if "error" in _data:
        return f"<h1>Error loading data</h1><pre>{_data['error']}</pre>", 500
    return render_template("index.html", allocations=ALLOCATIONS)


@app.route("/square/<square_id>")
def square_page(square_id):
    if square_id not in ALLOC_BY_ID:
        abort(404)
    return render_template("square.html", alloc=ALLOC_BY_ID[square_id])


@app.route("/api/data")
def api_data():
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    powers = _data["powers"]
    freqs = _data["freqs"]
    return jsonify({"freqs": freqs[::10].tolist(), "timestamps": _data["timestamps"], "powers": powers[:, ::10].tolist()})


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
    stats.update({"freq_min_mhz": 30.0, "freq_max_mhz": 54.0, "num_sweeps": int(_data["powers"].shape[0])})
    return jsonify(stats)


@app.route("/api/square/<square_id>")
def api_square(square_id):
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    if square_id not in _data["squares"]:
        abort(404)
    sq = _data["squares"][square_id]
    alloc = ALLOC_BY_ID[square_id]
    return jsonify({"id": square_id, "name": alloc["name"], "low": alloc["low"], "high": alloc["high"],
                    "freqs": sq["freqs"].tolist(), "timestamps": _data["timestamps"],
                    "powers": sq["powers"].tolist(), "num_cols": sq["num_cols"]})


@app.route("/api/square/<square_id>/histogram")
def api_square_histogram(square_id):
    if "error" in _data:
        return jsonify({"error": _data["error"]}), 500
    if square_id not in _data["squares"]:
        abort(404)
    edges, counts = compute_histogram(_data["squares"][square_id]["powers"].flatten())
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
    stats.update({"freq_min_mhz": alloc["low"], "freq_max_mhz": alloc["high"],
                  "num_sweeps": int(sq["powers"].shape[0]), "num_cols": sq["num_cols"]})
    return jsonify(stats)


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
