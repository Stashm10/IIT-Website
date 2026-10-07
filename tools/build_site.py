"""Generate the static site from data/index.json and data/settings.json:
index.html, band/<id>/index.html and about/index.html.

    python tools/build_site.py
"""
import calendar
import hashlib
import json
import os
import shutil
import statistics
import sys
from datetime import date, timedelta
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATES = os.path.join(HERE, "templates")
YEAR = 2018

CATEGORY_NAMES = {
    "broadcast": "Broadcast", "aeronautical": "Aeronautical", "satellite": "Satellite",
    "federal": "Federal", "amateur": "Amateur", "land-mobile": "Land mobile", "maritime": "Maritime",
    "radiolocation": "Radiolocation", "cellular": "Cellular", "public-safety": "Public safety",
}


def template(name):
    with open(os.path.join(TEMPLATES, name)) as fh:
        return fh.read()


def fill(text, **values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def asset_version():
    """Short hash of the assets so browsers fetch new CSS/JS after each rebuild."""
    h = hashlib.sha1()
    for name in sorted(os.listdir(os.path.join(REPO, "assets"))):
        with open(os.path.join(REPO, "assets", name), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:10]


def mhz(x):
    """A frequency exactly as written in bands.json: no rounding, no trailing zeros (30.0 -> '30').
    str() of a float is its shortest exact form, so 156.2475 stays 156.2475."""
    text = str(x)
    return text.rstrip("0").rstrip(".") if "." in text else text


def band_range(b):
    return f"{mhz(b['low_mhz'])}–{mhz(b['high_mhz'])}"


def coverage_html(dates):
    observed = set(dates)
    out = []
    for m in range(1, 13):
        n_days = calendar.monthrange(YEAR, m)[1]
        cells = "".join(
            f'<span class="cov-day{" on" if f"{YEAR}-{m:02d}-{d:02d}" in observed else ""}" '
            f'title="{calendar.month_abbr[m]} {d}"></span>'
            for d in range(1, n_days + 1))
        count = sum(1 for d in observed if d.startswith(f"{YEAR}-{m:02d}"))
        out.append(f'<div class="cov-month"><b>{calendar.month_name[m]}</b>'
                   f'<div class="cov-days">{cells}</div>{count} of {n_days} days</div>')
    return "\n".join(out)


def group_html(group, bands):
    span = group["high_mhz"] - group["low_mhz"]
    segs, items, ticks = [], [], []
    last_tick = -1.0
    for b in bands:
        share = (b["high_mhz"] - b["low_mhz"]) / span
        title = escape(f"{b['name']} — {band_range(b)} MHz")
        segs.append(f'<a class="band-seg cat-{b["category"]}" style="flex-grow:{share:.4f}" '
                    f'href="band/{b["id"]}/" title="{title}" aria-label="{title}">'
                    f'<span class="seg-label" aria-hidden="true">{escape(band_range(b))}</span></a>')
        items.append(f'<a href="band/{b["id"]}/" class="cat-{b["category"]}"><span class="cat-dot"></span>'
                     f'<span class="bl-name">{escape(b["name"])}</span>'
                     f'<span class="bl-range">{band_range(b)} MHz</span></a>')
    # Tick labels at band edges, skipping ones that would collide.
    edges = [group["low_mhz"]] + [b["high_mhz"] for b in bands]
    for i, edge in enumerate(edges):
        pos = (edge - group["low_mhz"]) / span
        if i in (0, len(edges) - 1) or (pos - last_tick >= 0.06 and 1 - pos >= 0.06):
            ticks.append(f'<span style="left:{pos * 100:.2f}%">{mhz(edge)}</span>')
            last_tick = pos
    return f"""  <section class="card group" id="{group['id']}">
    <div class="group-head"><h2>{escape(group['label'])}</h2><p>{escape(group['description'])}</p></div>
    <div class="band-bar">{''.join(segs)}</div>
    <div class="band-ticks" aria-hidden="true">{''.join(ticks)}</div>
    <div class="band-list">{''.join(items)}</div>
  </section>"""


def chrome(root):
    """Header, notice bar and footer shared by every page; `root` is the path back to the site root."""
    return {"header": template("header.html"), "notice": template("notice.html"),
            "footer": fill(template("footer.html"), root=root)}


def about_page(index, settings, v):
    """about/index.html: what the data is, how it is processed, coverage and limitations."""
    bands = index["bands"].values()
    observed = set(index["dates"])
    year_days = [date(YEAR, 1, 1) + timedelta(n) for n in range((date(YEAR + 1, 1, 1) - date(YEAR, 1, 1)).days)]
    missing = [d.isoformat() for d in year_days if d.isoformat() not in observed]
    partial = sorted((d, n) for d, n in index["sweeps"].items() if n < 100)
    used = {f"{mhz(b['subband']['start_mhz'])}-{mhz(b['subband']['stop_mhz'])}" for b in bands}
    steps = [settings["subbands"][k]["periods"][0]["freq_step_khz"] for k in used]
    interval = settings["typical_sweep_interval_s"]

    def day(d):
        return f"{calendar.month_abbr[int(d[5:7])]} {int(d[8:])}"

    month_rows = "".join(
        f"<tr><td>{calendar.month_name[m]}</td><td>"
        f"{sum(1 for d in observed if d.startswith(f'{YEAR}-{m:02d}'))} of {calendar.monthrange(YEAR, m)[1]}</td></tr>"
        for m in range(1, 13))
    unreadable = [(d, f) for d, files in sorted(index.get("unreadable", {}).items()) for f in files]
    draft = index["status"].upper().startswith("DRAFT")
    return fill(
        template("about.html"), v=v, **chrome("../"), year=YEAR,
        num_bands=len(index["bands"]), num_groups=len(index["groups"]),
        low_mhz=mhz(min(b["low_mhz"] for b in bands)), high_mhz=mhz(max(b["high_mhz"] for b in bands)),
        sweeps_per_day=int(statistics.median(index["sweeps"].values())),
        interval_min=f"{interval / 60:.1f}", interval_s=f"{interval:g}",
        draft_sentence=" The breakdown inside each group is provisional and awaiting confirmation." if draft else "",
        num_days=len(observed), days_in_year=len(year_days), month_rows=month_rows,
        num_missing=len(missing), missing_dates="".join(f"<li>{day(d)}</li>" for d in missing),
        partial_days="".join(f"<li>{day(d)}: {n} sweeps</li>" for d, n in partial),
        num_unreadable=len(unreadable),
        unreadable_files="".join(f"<li>{day(d)}: <code>{escape(f)}</code></li>" for d, f in unreadable),
        step_min=mhz(min(steps)), step_max=mhz(max(steps)),
        min_points=min(b["num_points"] for b in bands),
    )


def band_page(band, group, v):
    sub = band["subband"]
    note = (f'<span class="meta-chip">Note: {escape(band["note"])}</span>' if band.get("note") else "")
    return fill(
        template("band.html"),
        **chrome("../../"), v=v, id=band["id"], name=escape(band["name"]), range=band_range(band),
        group_id=group["id"], group_label=escape(f"Group {group['label']}"),
        category=CATEGORY_NAMES[band["category"]], cat_class=f"cat-{band['category']}",
        services=escape(band["services"]), subband=f"{mhz(sub['start_mhz'])}–{mhz(sub['stop_mhz'])}",
        num_points=band.get("num_points", "–"), note=note,
    )


def main():
    with open(os.path.join(REPO, "data", "index.json")) as fh:
        index = json.load(fh)
    settings_path = os.path.join(REPO, "data", "settings.json")
    if not os.path.exists(settings_path):
        sys.exit("data/settings.json is missing: run tools/build_settings.py first.")
    with open(settings_path) as fh:
        settings = json.load(fh)
    v = asset_version()
    bands = index["bands"]

    # Frequency-point counts come from any band file (constant through the year).
    for band_id, band in bands.items():
        with open(os.path.join(REPO, "data", "bands", f"{band_id}.json")) as fh:
            days = json.load(fh)["days"]
        band["num_points"] = days[0]["num_points"] if days else "–"

    groups_html = "\n".join(group_html(g, [bands[i] for i in g["band_ids"]]) for g in index["groups"])
    legend = "".join(f'<span class="cat-{c}"><span class="cat-dot"></span>{CATEGORY_NAMES[c]}</span>'
                     for c in index["categories"])
    with open(os.path.join(REPO, "index.html"), "w") as fh:
        fh.write(fill(template("index.html"), **chrome(""), v=v, num_days=len(index["dates"]), coverage=coverage_html(index["dates"]),
                      legend=legend, groups=groups_html))

    # Pages are overwritten in place (deleting and recreating the folder makes synced
    # folders such as iCloud Desktop leave "name 2" copies); stale band pages are removed.
    band_dir = os.path.join(REPO, "band")
    os.makedirs(band_dir, exist_ok=True)
    for name in os.listdir(band_dir):
        if name not in bands and os.path.isdir(os.path.join(band_dir, name)):
            shutil.rmtree(os.path.join(band_dir, name))
    group_of = {i: g for g in index["groups"] for i in g["band_ids"]}
    for band_id, band in bands.items():
        os.makedirs(os.path.join(band_dir, band_id), exist_ok=True)
        with open(os.path.join(band_dir, band_id, "index.html"), "w") as fh:
            fh.write(band_page(band, group_of[band_id], v))

    os.makedirs(os.path.join(REPO, "about"), exist_ok=True)
    with open(os.path.join(REPO, "about", "index.html"), "w") as fh:
        fh.write(about_page(index, settings, v))
    print(f"wrote index.html, {len(bands)} band pages and about/index.html")


if __name__ == "__main__":
    main()
