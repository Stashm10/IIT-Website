"""Core helpers: day keys, band masks, and per-band power statistics.

Histogram bins are fixed (bands.json "histogram_bins": -150 to +20 dBm, 0.5 dB)
so that daily histograms can be summed exactly into monthly / yearly ones.
"""
import re

import numpy as np

BIN_LOW, BIN_HIGH, BIN_WIDTH = -150.0, 20.0, 0.5
EDGES = np.round(np.arange(BIN_LOW, BIN_HIGH + BIN_WIDTH / 2, BIN_WIDTH), 2)
NUM_BINS = len(EDGES) - 1


def day_key(filename):
    """'IITSO_20180101000307_(30-6000_MHz).h5' -> '2018-01-01'."""
    m = re.search(r"IITSO_(\d{4})(\d{2})(\d{2})", filename)
    if not m:
        raise ValueError(f"not an IITSO file name: {filename}")
    return f"{m[1]}-{m[2]}-{m[3]}"


def band_columns(freqs_mhz, low_mhz, high_mhz):
    """Boolean mask of frequency points inside the half-open band [low, high)."""
    return (freqs_mhz >= low_mhz) & (freqs_mhz < high_mhz)


def band_stats(values):
    """Summary statistics + sparse fixed-bin histogram of all readings in a band."""
    v = np.asarray(values, dtype=np.float64).ravel()
    # Readings outside the bin range (never seen in practice) land in the edge bins.
    counts, _ = np.histogram(np.clip(v, BIN_LOW, BIN_HIGH - 1e-9), bins=EDGES)
    nonzero = np.nonzero(counts)[0]
    first, last = int(nonzero[0]), int(nonzero[-1]) + 1
    p10, median, p90 = np.percentile(v, [10, 50, 90])

    def r(x):
        return round(float(x), 4)

    return {
        "readings": int(v.size),
        "sum": float(v.sum()),
        "min": r(v.min()),
        "max": r(v.max()),
        "mean": r(v.mean()),
        "median": r(median),
        "p10": r(p10),
        "p90": r(p90),
        "peak_bin_low": float(EDGES[int(counts.argmax())]),
        "hist": {"o": first, "c": counts[first:last].tolist()},
    }


def dense(hist):
    """Expand a sparse {"o": offset, "c": counts} histogram to all NUM_BINS bins."""
    d = np.zeros(NUM_BINS, dtype=np.int64)
    d[hist["o"]:hist["o"] + len(hist["c"])] = hist["c"]
    return d
