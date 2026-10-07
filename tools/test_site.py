"""Band limits on the generated pages must match bands.json exactly (no rounding)."""
import glob
import json
import os
import re

import pytest

from build_site import mhz

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def exact(raw):
    """A number as written in bands.json, without trailing zeros ('30.0' -> '30')."""
    return raw.rstrip("0").rstrip(".") if "." in raw else raw


def plan_limits():
    """Every band, group and sub-band limit in bands.json, as the text written there."""
    with open(os.path.join(HERE, "bands.json")) as fh:
        plan = json.load(fh, parse_float=str, parse_int=str)
    bands, limits = [], set()
    for g in plan["groups"]:
        limits |= {exact(g["low_mhz"]), exact(g["high_mhz"])}
        for b in g["bands"]:
            lo, hi = exact(b["low_mhz"]), exact(b["high_mhz"])
            bands.append((b["id"], lo, hi))
            limits |= {lo, hi, exact(b["subband"]["start_mhz"]), exact(b["subband"]["stop_mhz"])}
    return bands, limits


@pytest.mark.parametrize("value, expected", [
    (44, "44"), (46.6, "46.6"), (117.975, "117.975"), (156.2475, "156.2475"),
    (462.5375, "462.5375"), (30.0, "30"),
])
def test_mhz_prints_values_exactly(value, expected):
    assert mhz(value) == expected


def test_mhz_matches_every_value_in_bands_json():
    with open(os.path.join(HERE, "bands.json")) as fh:
        plan = json.load(fh, parse_float=str, parse_int=str)
    for g in plan["groups"]:
        for b in g["bands"]:
            for raw in (b["low_mhz"], b["high_mhz"]):
                assert mhz(float(raw)) == exact(raw)


RANGE = re.compile(r"(\d+(?:\.\d+)?)–(\d+(?:\.\d+)?)")


def allowed_range(a, b, limits):
    """A range is fine if both ends are plan limits, or it is quoted verbatim from bands.json text
    (e.g. a note such as 'Part of the 43.69–46.6 MHz allocation')."""
    if a in limits and b in limits:
        return True
    with open(os.path.join(HERE, "bands.json"), encoding="utf-8") as fh:
        return f"{a}\u2013{b}" in json.dumps(json.load(fh), ensure_ascii=False)


def page(path):
    with open(os.path.join(REPO, path), encoding="utf-8") as fh:
        return fh.read()


def test_overview_shows_every_band_limit_exactly():
    html = page("index.html")
    bands, limits = plan_limits()
    for band_id, lo, hi in bands:
        assert f'<span class="bl-range">{lo}–{hi} MHz</span>' in html, band_id
        assert f'<span class="seg-label" aria-hidden="true">{lo}–{hi}</span>' in html, band_id
    for a, b in RANGE.findall(html):
        assert allowed_range(a, b, limits), f"{a}–{b} is not a band limit from bands.json"
    ticks = re.findall(r'<span style="left:[\d.]+%">([^<]+)</span>', html)
    assert ticks, "no tick labels found"
    for t in ticks:
        assert t in limits, f"tick {t} is not a band limit from bands.json"


def test_band_pages_show_limits_exactly():
    bands, limits = plan_limits()
    for band_id, lo, hi in bands:
        html = page(f"band/{band_id}/index.html")
        assert f"({lo}–{hi} MHz)" in html.split("</title>")[0], band_id
        for a, b in RANGE.findall(html):
            assert allowed_range(a, b, limits), f"{band_id}: {a}–{b} is not a limit from bands.json"
    assert len(glob.glob(os.path.join(REPO, "band", "*", "index.html"))) == len(bands)


NOTICE = "Research prototype by the IIT Spectrum Observatory project. This is not an official Illinois Tech web page."


def all_pages():
    return ["index.html"] + [
        os.path.relpath(p, REPO) for p in glob.glob(os.path.join(REPO, "band", "*", "index.html"))]


def test_every_page_has_notice_bar_and_footer():
    for path in all_pages():
        html = page(path)
        notice = html.index('<div class="site-notice"')
        assert notice > html.index("</header>"), f"{path}: notice must come right after the header"
        assert html.count(NOTICE) == 2, f"{path}: notice text should appear in the bar and the footer"
        assert '<footer class="site-footer">' in html, path
        assert "About the data" not in html and 'href="about/"' not in html and "../../about/" not in html, \
            f"{path}: link to the removed About page"


def plan_bands():
    with open(os.path.join(HERE, "bands.json")) as fh:
        plan = json.load(fh)
    return plan, [b for g in plan["groups"] for b in g["bands"]]


def test_stripes_match_allocations_for_every_band():
    from build_site import SECONDARY_SHARE
    from ntia import MARKER_COLORS, MARKER_NAMES, SERVICE_COLORS
    html = page("index.html")
    plan, bands = plan_bands()
    markers = plan["rules"]["category_markers"]
    for b in bands:
        seg = re.search(rf'<a class="band-seg[^"]*"[^>]*href="band/{re.escape(b["id"])}/".*?</a>', html).group(0)
        got = re.findall(r'<span style="background:(#[0-9a-f]{6});flex-grow:([\d.]+)"></span>', seg)
        primary = [a for a in b["allocations"] if a["status"] == "primary"]
        secondary = [a for a in b["allocations"] if a["status"] == "secondary"]
        rest = 100 * (1 - SECONDARY_SHARE * len(secondary))
        want = [(SERVICE_COLORS[a["service"]], rest / len(primary)) for a in primary]
        want += [(SERVICE_COLORS[a["service"]], 100 * SECONDARY_SHARE) for a in secondary]
        assert [(c, round(float(g), 3)) for c, g in got] == [(c, round(g, 3)) for c, g in want], b["id"]
        if b["category"] in markers:
            assert "has-marker" in seg and f'class="seg-marker" style="background:{MARKER_COLORS[b["category"]]}"' in seg, b["id"]
            item = re.search(rf'<a href="band/{re.escape(b["id"])}/" title=.*?</a>', html).group(0)
            assert f'<span class="cat-tag">{MARKER_NAMES[b["category"]]}</span>' in item, b["id"]
        else:
            assert "seg-marker" not in seg and "has-marker" not in seg, b["id"]


def test_legend_lists_exactly_the_services_in_use():
    from build_site import LEGEND_NOTE
    from ntia import MARKER_NAMES
    html = page("index.html")
    plan, bands = plan_bands()
    used = sorted({a["service"] for b in bands for a in b["allocations"]})
    services_block = html.split('<div class="legend-title">Allocated services</div>')[1].split("</div>")[0]
    assert re.findall(r"</span></span>([^<]+)</span>", services_block) == used
    markers_block = html.split('<div class="legend-title">Markers</div>')[1].split("</div>")[0]
    assert re.findall(r'class="marker-swatch"[^>]*></span>([^<]+)</span>', markers_block) == [
        MARKER_NAMES[c] for c in plan["rules"]["category_markers"]]
    assert LEGEND_NOTE in html
    assert "cat-" not in html.replace("cat-tag", "")


def test_band_pages_write_services_from_allocations():
    from build_site import allocation_notes, services_text
    _, bands = plan_bands()
    for b in bands:
        html = page(f"band/{b['id']}/index.html")
        assert f"Services: <strong>{escape_html(services_text(b))}</strong>" in html, b["id"]
        for note in allocation_notes(b):
            assert escape_html(note) in html, b["id"]
    amateur = next(b for b in bands if b["id"] == "400-460--420-430")
    assert services_text(amateur) == "RADIOLOCATION, Amateur (secondary)"


def escape_html(text):
    from html import escape
    return escape(text)
