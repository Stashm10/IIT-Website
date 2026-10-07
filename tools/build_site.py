"""Generate the static site (index.html + band/<id>/index.html) from data/index.json.
Band pages load data/settings.json in the browser for the receiver-settings chips.

    python tools/build_site.py
"""
import calendar
import hashlib
import json
import os
import shutil
from html import escape

from ntia import MARKER_COLORS, MARKER_NAMES, SERVICE_COLORS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATES = os.path.join(HERE, "templates")
PLAN_DIR = os.environ.get("IIT_V2_DIR", HERE)  # where bands.json lives (same rule as build_data.py)
SECONDARY_SHARE = 0.2  # a secondary service's stripe: one fifth of the service area
LEGEND_NOTE = ("Stripe colours are adapted from the NTIA United States Frequency Allocations chart. "
               "Service names in CAPITALS are primary allocations; a thin stripe and lower-case name "
               "mark a secondary allocation.")
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


def stripe_layout(band):
    """[(allocation, share of the service area)] in drawing order, from the band's `allocations`:
    primary services in listed order share the area equally; secondary services follow below them
    as thin stripes (SECONDARY_SHARE each)."""
    primary = [a for a in band["allocations"] if a["status"] == "primary"]
    secondary = [a for a in band["allocations"] if a["status"] == "secondary"]
    rest = 1 - SECONDARY_SHARE * len(secondary)
    return [(a, rest / len(primary)) for a in primary] + [(a, SECONDARY_SHARE) for a in secondary]


def allocation_text(a):
    """'AERONAUTICAL MOBILE (R)' for a primary service, 'Amateur (secondary)' for a secondary one."""
    text = a["service"] if a["status"] == "primary" else a["service"].capitalize()
    if a.get("qualifier"):
        text += f" {a['qualifier']}"
    return text + (" (secondary)" if a["status"] == "secondary" else "")


def services_text(band):
    return ", ".join(allocation_text(a) for a, _ in stripe_layout(band))


def allocation_notes(band):
    return [f"{allocation_text(a)}: {a['note']}" for a, _ in stripe_layout(band) if a.get("note")]


def marker_of(band, markers):
    return band["category"] if band["category"] in markers else None


def stripes(band, cls):
    """The band's service stripes, top to bottom, sized by stripe_layout()."""
    cells = "".join(f'<span style="background:{SERVICE_COLORS[a["service"]]};flex-grow:{share * 100:g}"></span>'
                    for a, share in stripe_layout(band))
    return f'<span class="{cls}" title="{escape(services_text(band))}">{cells}</span>'


def legend_html(bands, markers):
    """Legend generated from bands.json: the services in use (alphabetical), the markers and a note."""
    used = sorted({a["service"] for b in bands for a in b["allocations"]})
    services = "".join(f'<span class="legend-item"><span class="svc-swatch"><span style="background:'
                       f'{SERVICE_COLORS[s]}"></span></span>{escape(s)}</span>' for s in used)
    marker_items = "".join(f'<span class="legend-item"><span class="marker-swatch" style="background:'
                           f'{MARKER_COLORS[c]}"></span>{escape(MARKER_NAMES[c])}</span>' for c in markers)
    return (f'<div class="legend-block"><div class="legend-title">Allocated services</div>'
            f'<div class="legend">{services}</div></div>'
            f'<div class="legend-block"><div class="legend-title">Markers</div>'
            f'<div class="legend">{marker_items}</div></div>'
            f'<p class="legend-note">{escape(LEGEND_NOTE)}</p>')


def group_html(group, bands, markers):
    span = group["high_mhz"] - group["low_mhz"]
    segs, items, ticks = [], [], []
    last_tick = -1.0
    for b in bands:
        share = (b["high_mhz"] - b["low_mhz"]) / span
        marker = marker_of(b, markers)
        lines = [f"{b['name']} — {band_range(b)} MHz"]
        lines += [allocation_text(a) for a, _ in stripe_layout(b)] + allocation_notes(b)
        lines += [f"Category: {MARKER_NAMES[marker]}"] if marker else []
        title = "&#10;".join(escape(line) for line in lines)
        label = escape(f"{b['name']}, {band_range(b)} MHz. Services: {services_text(b)}"
                       + (f". {MARKER_NAMES[marker]}" if marker else ""))
        strip = f'<span class="seg-marker" style="background:{MARKER_COLORS[marker]}"></span>' if marker else ""
        segs.append(f'<a class="band-seg{" has-marker" if marker else ""}" style="flex-grow:{share:.4f}" '
                    f'href="band/{b["id"]}/" title="{title}" aria-label="{label}">{stripes(b, "seg-stripes")}{strip}'
                    f'<span class="seg-label" aria-hidden="true">{escape(band_range(b))}</span></a>')
        tag = f'<span class="cat-tag">{escape(MARKER_NAMES[marker])}</span>' if marker else ""
        items.append(f'<a href="band/{b["id"]}/" title="{escape(services_text(b))}">{stripes(b, "svc-swatch")}'
                     f'<span class="bl-name">{escape(b["name"])}{tag}'
                     f'<span class="sr-only"> Services: {escape(services_text(b))}</span></span>'
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


def chrome():
    """Header, notice bar and footer shared by every page."""
    return {"header": template("header.html"), "notice": template("notice.html"),
            "footer": template("footer.html")}


def band_page(band, group, v):
    sub = band["subband"]
    notes = allocation_notes(band)
    alloc_notes = (f'<span class="meta-chip">Allocation notes: {escape(" ".join(notes))}</span>' if notes else "")
    note = (f'<span class="meta-chip">Note: {escape(band["note"])}</span>' if band.get("note") else "")
    return fill(
        template("band.html"),
        **chrome(), v=v, id=band["id"], name=escape(band["name"]), range=band_range(band),
        group_id=group["id"], group_label=escape(f"Group {group['label']}"),
        category=CATEGORY_NAMES[band["category"]], swatch=stripes(band, "svc-swatch"),
        services=escape(services_text(band)), alloc_notes=alloc_notes, subband=f"{mhz(sub['start_mhz'])}–{mhz(sub['stop_mhz'])}",
        num_points=band.get("num_points", "–"), note=note,
    )


def main():
    with open(os.path.join(REPO, "data", "index.json")) as fh:
        index = json.load(fh)
    v = asset_version()
    bands = index["bands"]

    # Frequency-point counts come from any band file (constant through the year).
    for band_id, band in bands.items():
        with open(os.path.join(REPO, "data", "bands", f"{band_id}.json")) as fh:
            days = json.load(fh)["days"]
        band["num_points"] = days[0]["num_points"] if days else "–"

    with open(os.path.join(PLAN_DIR, "bands.json")) as fh:
        markers = json.load(fh)["rules"]["category_markers"]
    groups_html = "\n".join(group_html(g, [bands[i] for i in g["band_ids"]], markers) for g in index["groups"])
    legend = legend_html(bands.values(), markers)
    with open(os.path.join(REPO, "index.html"), "w") as fh:
        fh.write(fill(template("index.html"), **chrome(), v=v, num_days=len(index["dates"]), coverage=coverage_html(index["dates"]),
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
    print(f"wrote index.html and {len(bands)} band pages")


if __name__ == "__main__":
    main()
