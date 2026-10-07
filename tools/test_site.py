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
    return ["index.html", "about/index.html"] + [
        os.path.relpath(p, REPO) for p in glob.glob(os.path.join(REPO, "band", "*", "index.html"))]


def test_every_page_has_notice_bar_and_footer():
    for path in all_pages():
        html = page(path)
        notice = html.index('<div class="site-notice"')
        assert notice > html.index("</header>"), f"{path}: notice must come right after the header"
        assert html.count(NOTICE) == 2, f"{path}: notice text should appear in the bar and the footer"
        assert '<footer class="site-footer">' in html and "about/\">About the data</a>" in html, path


def test_about_page_draft_sentence_follows_status():
    import json as _json
    from build_site import about_page
    with open(os.path.join(REPO, "data", "index.json")) as fh:
        index = _json.load(fh)
    with open(os.path.join(REPO, "data", "settings.json")) as fh:
        settings = _json.load(fh)
    for b in index["bands"].values():
        b["num_points"] = 10
    sentence = "The breakdown inside each group is provisional and awaiting confirmation."
    index["status"] = "DRAFT - proposal"
    assert sentence in about_page(index, settings, "v")
    index["status"] = "Confirmed by the observatory team"
    assert sentence not in about_page(index, settings, "v")


def test_about_page_has_credit_placeholder_only():
    html = page("about/index.html")
    assert "[[CREDITS — to be added]]" in html
