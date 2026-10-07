import numpy as np
from spectrum import day_key, band_stats, dense, band_columns, EDGES


def test_day_key():
    assert day_key("IITSO_20181214080327_(30-6000_MHz).h5") == "2018-12-14"


def test_edges_match_bands_json():
    assert len(EDGES) == 341 and EDGES[0] == -150.0 and EDGES[-1] == 20.0


def test_band_stats_and_sparse_roundtrip():
    v = np.array([-100.2, -100.1, -90.0, -89.9])
    s = band_stats(v)
    assert s["readings"] == 4 and s["min"] == -100.2 and s["max"] == -89.9
    d = dense(s["hist"])
    assert d.sum() == 4 and len(d) == 340
    assert d[int((-100.5 + 150) / 0.5)] == 2
    assert s["peak_bin_low"] == -100.5


def test_band_columns_half_open():
    f = np.array([44.0, 44.5, 46.6])
    assert band_columns(f, 44, 46.6).tolist() == [True, True, False]
