"""Service and marker colors: coverage, provenance and separation."""
import itertools
import json
import os

from build_site import stripe_layout
from ntia import ADJUSTED, MARKER_COLORS, OFFICIAL, SERVICE_COLORS, oklab_distance

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "bands.json")) as fh:
    PLAN = json.load(fh)
BANDS = [b for g in PLAN["groups"] for b in g["bands"]]
USED = sorted({a["service"] for b in BANDS for a in b["allocations"]})
# Fill of the NTIA chart's federal / shared / non-federal "activity code" boxes (read from the PDF).
ACTIVITY_CODE = ["#ee334e", "#231f20", "#00b185"]


def touching_pairs():
    """Service pairs whose stripes touch: stacked in one segment, or overlapping across neighbours."""
    touch = set()
    for g in PLAN["groups"]:
        segs = []
        for b in g["bands"]:
            y, spans = 0.0, []
            for a, share in stripe_layout(b):
                spans.append((a["service"], y, y + share))
                y += share
            segs.append(spans)
        for spans in segs:
            touch |= {tuple(sorted((a, b))) for (a, _, _), (b, _, _) in zip(spans, spans[1:]) if a != b}
        for left, right in zip(segs, segs[1:]):
            touch |= {tuple(sorted((a, b))) for a, a0, a1 in left for b, b0, b1 in right
                      if a != b and min(a1, b1) - max(a0, b0) > 1e-9}
    return touch


def test_one_color_per_ntia_service():
    assert set(SERVICE_COLORS) == set(PLAN["rules"]["ntia_services"])
    assert set(OFFICIAL) == set(PLAN["rules"]["ntia_services"])


def test_unadjusted_colors_are_official_and_adjustments_are_explained():
    for name, color in SERVICE_COLORS.items():
        if name in ADJUSTED:
            assert color == ADJUSTED[name][0] and ADJUSTED[name][1], name
        else:
            assert color == OFFICIAL[name], name
    assert {"FIXED", "MOBILE", "LAND MOBILE"}.isdisjoint(ADJUSTED)


def test_every_used_service_pair_is_distinguishable():
    touch = touching_pairs()
    for a, b in itertools.combinations(USED, 2):
        need = 15 if (a, b) in touch else 10
        assert oklab_distance(SERVICE_COLORS[a], SERVICE_COLORS[b]) >= need, (a, b)
    assert ("BROADCASTING", "LAND MOBILE") in touch


def test_markers_differ_from_services_each_other_and_the_ntia_activity_code():
    assert set(MARKER_COLORS) == set(PLAN["rules"]["category_markers"])
    for cat, color in MARKER_COLORS.items():
        for s in USED:
            assert oklab_distance(color, SERVICE_COLORS[s]) >= 15, (cat, s)
        for code in ACTIVITY_CODE:
            assert oklab_distance(color, code) >= 15, (cat, code)
    for a, b in itertools.combinations(MARKER_COLORS.values(), 2):
        assert oklab_distance(a, b) >= 15


def test_secondary_services_get_a_thin_stripe_below_the_primaries():
    band = next(b for b in BANDS if b["id"] == "400-460--420-430")
    layout = [(a["service"], a["status"], round(share, 3)) for a, share in stripe_layout(band)]
    assert layout == [("RADIOLOCATION", "primary", 0.8), ("AMATEUR", "secondary", 0.2)]
    for b in BANDS:
        assert abs(sum(share for _, share in stripe_layout(b)) - 1) < 1e-9
