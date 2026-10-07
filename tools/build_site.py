"""Generate the static site (index.html + band/<id>/index.html) from data/index.json.

    python tools/build_site.py
"""
import calendar
import hashlib
import json
import os
import shutil
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
    return f"{x:g}"


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


def unreadable_html(index):
    bad = index.get("unreadable", {})
    if not bad:
        return ""
    files = ", ".join(f"{date} ({', '.join(names)})" for date, names in sorted(bad.items()))
    return f" Source files skipped because they are damaged or incomplete: {escape(files)}."


def group_html(group, bands):
    span = group["high_mhz"] - group["low_mhz"]
    segs, items, ticks = [], [], []
    last_tick = -1.0
    for b in bands:
        share = (b["high_mhz"] - b["low_mhz"]) / span
        label = escape(band_range(b)) if share >= 0.09 else ""
        title = escape(f"{b['name']} — {band_range(b)} MHz")
        segs.append(f'<a class="band-seg cat-{b["category"]}" style="flex-grow:{share:.4f}" '
                    f'href="band/{b["id"]}/" title="{title}" aria-label="{title}">{label}</a>')
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


def band_page(band, group, header, v):
    sub = band["subband"]
    note = (f'<span class="meta-chip">Note: {escape(band["note"])}</span>' if band.get("note") else "")
    return fill(
        template("band.html"),
        header=header, v=v, id=band["id"], name=escape(band["name"]), range=band_range(band),
        group_id=group["id"], group_label=escape(f"Group {group['label']}"),
        category=CATEGORY_NAMES[band["category"]], cat_class=f"cat-{band['category']}",
        services=escape(band["services"]), subband=f"{mhz(sub['start_mhz'])}–{mhz(sub['stop_mhz'])}",
        num_points=band.get("num_points", "–"), note=note,
    )


def main():
    with open(os.path.join(REPO, "data", "index.json")) as fh:
        index = json.load(fh)
    header = template("header.html")
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
        fh.write(fill(template("index.html"), header=header, v=v, num_days=len(index["dates"]), coverage=coverage_html(index["dates"]),
                      legend=legend, groups=groups_html, unreadable=unreadable_html(index)))

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
            fh.write(band_page(band, group_of[band_id], header, v))
    print(f"wrote index.html and {len(bands)} band pages")


if __name__ == "__main__":
    main()
