"""Receiver-settings pass: attribute reading and period / change detection."""
import h5py
import numpy as np

from build_settings import freq_step_khz, mhz_key, read_file, summarize_subband, varying_attributes

BASE = {"start_freq": 30e6, "stop_freq": 54e6, "num_points": 8001, "rbw": 3000.0, "vbw": False,
        "atten": 0, "ref_level": -60, "avg_len": 1, "name": "TV channels 2-3"}


def info(sweeps=123, **changes):
    return {"settings": {**BASE, **changes}, "sweeps": sweeps, "interval_s": 704.6, "sweep_time_s": 2.86}


def test_mhz_key():
    assert mhz_key(30.0, 54.0) == "30-54"
    assert mhz_key(760.0, 780.0) == "760-780"


def test_freq_step_uses_num_points_minus_one():
    assert freq_step_khz(BASE) == 3.0


def test_read_file_needs_only_attributes_and_times(tmp_path):
    path = tmp_path / "f.h5"
    with h5py.File(path, "w") as f:
        f.create_group("sessions/0").attrs["location"] = "IIT Tower"
        g = f.create_group("sessions/0/spectrum/0")
        for k, v in BASE.items():
            g.attrs[k] = v
        g.attrs["index"] = 0
        g["start_time"] = np.array([0.0, 700.0, 1405.0])
        g["sweep_time"] = np.array([2.8, 2.9, 3.0])
        # deliberately no "powers" dataset: the pass must not need it
    out = read_file(str(path), [0])
    sb = out["subbands"][0]
    assert sb["settings"]["atten"] == 0 and sb["settings"]["name"] == "TV channels 2-3"
    assert sb["settings"]["index"] == 0
    assert sb["sweeps"] == 3 and sb["interval_s"] == 702.5 and sb["sweep_time_s"] == 2.9
    assert out["groups"]["/sessions/0"] == {"location": "IIT Tower"}


def test_periods_and_changes():
    days = [("2018-01-01", [("a", info())]),
            ("2018-01-02", [("b", info())]),
            ("2018-01-04", [("c", info(atten=10))]),   # a gap in observed dates does not split a period
            ("2018-01-05", [("d", info(atten=10))]),
            ("2018-01-06", [("e", info())])]
    s = summarize_subband(days)
    assert [(p["from"], p["to"], p["days"]) for p in s["periods"]] == [
        ("2018-01-01", "2018-01-02", 2), ("2018-01-04", "2018-01-05", 2), ("2018-01-06", "2018-01-06", 1)]
    assert s["changes"] == [
        {"date": "2018-01-04", "previous_date": "2018-01-02", "field": "atten", "old": 0, "new": 10},
        {"date": "2018-01-06", "previous_date": "2018-01-05", "field": "atten", "old": 10, "new": 0}]
    assert s["periods"][0]["freq_step_khz"] == 3.0 and s["mixed_days"] == []


def test_constant_year_is_one_period():
    s = summarize_subband([(f"2018-01-0{d}", [("f", info())]) for d in range(1, 6)])
    assert len(s["periods"]) == 1 and s["changes"] == []


def test_mixed_day_is_reported_and_uses_the_larger_file():
    days = [("2018-06-14", [("short", info(sweeps=10, ref_level=-50)), ("long", info(sweeps=113))])]
    s = summarize_subband(days)
    assert s["mixed_days"][0]["date"] == "2018-06-14"
    assert set(s["mixed_days"][0]["files"]) == {"short", "long"}
    assert s["periods"][0]["settings"]["ref_level"] == -60


def test_varying_attributes():
    files = [("2018-01-01", "a", {"/sessions/0": {"sensor": "X", "lat": 41.8}}),
             ("2018-01-02", "b", {"/sessions/0": {"sensor": "X", "lat": 41.8}}),
             ("2018-01-03", "c", {"/sessions/0": {"sensor": "Y", "lat": 41.8}})]
    out = varying_attributes(files)
    assert out == [{"path": "/sessions/0", "name": "sensor",
                    "changes": [{"date": "2018-01-03", "file": "c", "old": "X", "new": "Y"}]}]
