"""Service colors for the band stripes, keyed by NTIA service name (bands.json rules.ntia_services).

OFFICIAL holds the fill of each box in the "Radio Services Color Legend" of the NTIA United States
Frequency Allocations chart (January 2016),
https://www.ntia.gov/sites/default/files/publications/january_2016_spectrum_wall_chart_0.pdf
read from the PDF's vector drawing commands (not sampled from pixels). The legend calls
METEOROLOGICAL AIDS just "METEOROLOGICAL".

A few official colors are too close to tell apart on the site (OKLab distance x100: under 15 for
colors that touch on the site, under 10 for any other pair). ADJUSTED lists every color changed for
that reason; each stays in the same color family. SERVICE_COLORS is what the site uses.
"""
OFFICIAL = {
    "AERONAUTICAL MOBILE": "#0fafe2",
    "AERONAUTICAL MOBILE SATELLITE": "#97c9ec",
    "AERONAUTICAL RADIONAVIGATION": "#c05018",
    "AMATEUR": "#009370",
    "AMATEUR SATELLITE": "#d5ebe0",
    "BROADCASTING": "#3197b9",
    "BROADCASTING SATELLITE": "#62bb46",
    "EARTH EXPLORATION SATELLITE": "#f79239",
    "FIXED": "#df068c",
    "FIXED SATELLITE": "#c183b9",
    "INTER-SATELLITE": "#ffe276",
    "LAND MOBILE": "#00a2b3",
    "LAND MOBILE SATELLITE": "#74ccd4",
    "MARITIME MOBILE": "#e9e5c3",
    "MARITIME MOBILE SATELLITE": "#99c9bd",
    "MARITIME RADIONAVIGATION": "#4d8f76",
    "METEOROLOGICAL AIDS": "#efd7c2",
    "METEOROLOGICAL SATELLITE": "#965d10",
    "MOBILE": "#e9d3e7",
    "MOBILE SATELLITE": "#9b5ba4",
    "RADIO ASTRONOMY": "#fff200",
    "RADIODETERMINATION SATELLITE": "#faab54",
    "RADIOLOCATION": "#f3cf1f",
    "RADIOLOCATION SATELLITE": "#c4a005",
    "RADIONAVIGATION": "#abbd26",
    "RADIONAVIGATION SATELLITE": "#e8ea7c",
    "SPACE OPERATION": "#a44138",
    "SPACE RESEARCH": "#e68e96",
    "STANDARD FREQUENCY AND TIME SIGNAL": "#8e979d",
    "STANDARD FREQUENCY AND TIME SIGNAL SATELLITE": "#b4b6b8",
}

# service: (site color, why it was changed). Found by a minimal-change search: the three most-used
# colors (FIXED, MOBILE, LAND MOBILE) were kept, hue changes limited to 20 degrees.
ADJUSTED = {
    "AERONAUTICAL MOBILE": ("#66c7fc", "official color was 7.3 from LAND MOBILE, 7.9 from BROADCASTING"),
    "AMATEUR": ("#098b4a", "official color was 10.0 from LAND MOBILE"),
    "AMATEUR SATELLITE": ("#a4fecd", "official color was 4.1 from MARITIME MOBILE, 5.8 from METEOROLOGICAL AIDS"),
    "BROADCASTING": ("#036fb0", "official color was 3.7 from LAND MOBILE, 7.9 from AERONAUTICAL MOBILE"),
    "EARTH EXPLORATION SATELLITE": ("#f68b2d", "moved to make room for a neighbouring adjusted color"),
    "MARITIME MOBILE": ("#fcf59f", "official color was 3.6 from METEOROLOGICAL AIDS, 4.1 from AMATEUR SATELLITE"),
    "METEOROLOGICAL AIDS": ("#fcc897", "official color was 3.6 from MARITIME MOBILE, 5.5 from MOBILE"),
    "METEOROLOGICAL SATELLITE": ("#8f6405", "official color was 8.2 from AERONAUTICAL RADIONAVIGATION, 8.7 from SPACE OPERATION"),
    "RADIO ASTRONOMY": ("#f8f700", "official color was 7.4 from RADIONAVIGATION SATELLITE, 9.2 from RADIOLOCATION"),
    "RADIONAVIGATION SATELLITE": ("#ade12f", "official color was 7.4 from RADIO ASTRONOMY, 7.5 from RADIOLOCATION"),
    "SPACE OPERATION": ("#a52b3c", "official color was 7.6 from AERONAUTICAL RADIONAVIGATION, 8.7 from METEOROLOGICAL SATELLITE"),
    "STANDARD FREQUENCY AND TIME SIGNAL SATELLITE": ("#a8b1b8", "official color was 12.6 from METEOROLOGICAL AIDS"),
}

SERVICE_COLORS = {**OFFICIAL, **{name: color for name, (color, _) in ADJUSTED.items()}}

# Category marker strips (the site's own markers, not the NTIA chart's federal/non-federal code).
MARKER_COLORS = {"federal": "#505058", "cellular": "#3000a8", "public-safety": "#680828"}
MARKER_NAMES = {"federal": "Federal", "cellular": "Cellular", "public-safety": "Public safety"}


def oklab_distance(hex_a, hex_b):
    """Euclidean distance in OKLab, x100 (about 2 is the smallest visible difference)."""
    def lab(h):
        rgb = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)
        l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
        m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
        s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
        return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)
    a, b = lab(hex_a), lab(hex_b)
    return 100 * sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
