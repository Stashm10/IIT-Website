"""Day grouping and bad-file handling, using small synthetic files in a temp folder."""
import h5py
import numpy as np
import pytest

from build_data import files_by_day, process_day

BANDS = [{"id": "b", "low_mhz": 31, "high_mhz": 32, "subband": {"index_in_reference_file": 0}}]


def make_file(path, sweeps, value=-100.0):
    with h5py.File(path, "w") as f:
        ds = f.create_group("sessions/0/spectrum/0")
        ds.attrs["start_freq"], ds.attrs["stop_freq"], ds.attrs["num_points"] = 30e6, 54e6, 25
        ds["powers"] = np.full((sweeps, 25), value, dtype=np.float32)
    return str(path)


def test_files_by_day_pools_dates_and_drops_duplicate_copies(tmp_path):
    for name in ["IITSO_20180821000100_(30-6000_MHz).h5", "IITSO_20180821133309_(30-6000_MHz).h5",
                 "IITSO_20180821133309_(30-6000_MHz) (1).h5", "IITSO_20180822000100_(30-6000_MHz).h5"]:
        (tmp_path / name).write_bytes(b"")
    days = files_by_day(str(tmp_path))
    assert list(days) == ["2018-08-21", "2018-08-22"]
    assert [p.rsplit("/", 1)[1] for p in days["2018-08-21"]] == [
        "IITSO_20180821000100_(30-6000_MHz).h5", "IITSO_20180821133309_(30-6000_MHz).h5"]


def test_process_day_skips_corrupt_and_incomplete_files(tmp_path):
    good = make_file(tmp_path / "IITSO_20180414220529_(30-6000_MHz).h5", sweeps=10)
    corrupt = tmp_path / "IITSO_20180414000502_(30-6000_MHz).h5"
    corrupt.write_bytes(b"\0" * 1024)
    empty = tmp_path / "IITSO_20180414130626_(30-6000_MHz).h5"
    with h5py.File(empty, "w"):
        pass
    day = process_day([str(corrupt), str(empty), good], BANDS)
    assert day["date"] == "2018-04-14"
    assert day["sweeps"] == 10 and day["bands"]["b"]["readings"] == 10 * day["bands"]["b"]["num_points"]
    assert day["files"] == ["IITSO_20180414220529_(30-6000_MHz).h5"]
    assert sorted(s["file"] for s in day["skipped"]) == sorted([corrupt.name, empty.name])


def test_process_day_raises_when_no_file_is_usable(tmp_path):
    corrupt = tmp_path / "IITSO_20180311111528_(30-6000_MHz).h5"
    corrupt.write_bytes(b"\0" * 1024)
    with pytest.raises(ValueError, match="no usable file"):
        process_day([str(corrupt)], BANDS)
