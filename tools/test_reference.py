"""Validation gate: Jan 1 2018 must reproduce reference_2018-01-01.json for every band."""
import glob
import json
import os

from build_data import DATA_DIR, V2_DIR, load_bands, process_day


def test_jan1_matches_reference():
    ref = json.load(open(os.path.join(V2_DIR, "reference_2018-01-01.json")))
    day = process_day(sorted(glob.glob(os.path.join(DATA_DIR, "IITSO_20180101*.h5"))), load_bands())
    assert day["sweeps"] == ref["sweeps_in_file"]
    assert len(ref["bands"]) == 91
    for rb in ref["bands"]:
        got = day["bands"][rb["id"]]
        assert got["num_points"] == rb["num_points"], rb["id"]
        assert got["readings"] == rb["num_readings"], rb["id"]
        assert got["peak_bin_low"] == rb["peak_bin_low_dbm"], rb["id"]
        for k in ["min", "max", "mean", "median", "p10", "p90"]:
            assert abs(got[k] - rb[k + "_dbm"]) < 0.01, (rb["id"], k, got[k], rb[k + "_dbm"])
