"""Every service in bands.json must map to an NTIA allocation-chart color."""
import json
import os

import pytest

from ntia import NTIA_COLORS, services

HERE = os.path.dirname(os.path.abspath(__file__))


def test_palette_has_all_30_ntia_services():
    assert len(NTIA_COLORS) == 30
    assert NTIA_COLORS["FIXED"] == "#df068c" and NTIA_COLORS["MOBILE"] == "#e9d3e7"
    assert NTIA_COLORS["LAND MOBILE"] == "#00a2b3" and NTIA_COLORS["AMATEUR"] == "#009370"


@pytest.mark.parametrize("text, expected", [
    ("FIXED, MOBILE", ["FIXED", "MOBILE"]),
    ("MOBILE except aeronautical mobile", ["MOBILE"]),
    ("AERONAUTICAL MOBILE (R)", ["AERONAUTICAL MOBILE"]),
    ("RADIOLOCATION, Amateur", ["RADIOLOCATION", "AMATEUR"]),
    ("AMATEUR, AMATEUR-SATELLITE", ["AMATEUR", "AMATEUR SATELLITE"]),
    ("MARITIME MOBILE, LAND MOBILE, MARITIME MOBILE (AIS)", ["MARITIME MOBILE", "LAND MOBILE"]),
    ("FIXED, MOBILE, MOBILE-SATELLITE (Earth-to-space); RADIONAVIGATION-SATELLITE (149.9–150.05)",
     ["FIXED", "MOBILE", "MOBILE SATELLITE", "RADIONAVIGATION SATELLITE"]),
    ("METEOROLOGICAL AIDS (radiosonde); EARTH EXPLORATION-SATELLITE and METEOROLOGICAL-SATELLITE uplinks in 401–403",
     ["METEOROLOGICAL", "EARTH EXPLORATION SATELLITE", "METEOROLOGICAL SATELLITE"]),
    ("STANDARD FREQUENCY AND TIME SIGNAL-SATELLITE, METEOROLOGICAL AIDS",
     ["STANDARD FREQUENCY AND TIME SIGNAL SATELLITE", "METEOROLOGICAL"]),
    ("SPACE RESEARCH (space-to-Earth)", ["SPACE RESEARCH"]),
])
def test_services_are_parsed_to_ntia_names(text, expected):
    assert services(text) == expected


def test_unknown_service_is_an_error():
    with pytest.raises(ValueError, match="no NTIA color"):
        services("FIXED, TELEPATHY")


def test_every_band_in_the_plan_has_ntia_colors():
    with open(os.path.join(HERE, "bands.json")) as fh:
        plan = json.load(fh)
    for g in plan["groups"]:
        for b in g["bands"]:
            names = services(b["services"])
            assert names, b["id"]
            assert all(n in NTIA_COLORS for n in names), b["id"]
