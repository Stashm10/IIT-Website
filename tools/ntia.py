"""Radio-service colors of the official U.S. Frequency Allocation Chart (NTIA).

Colors were read from the fill of each box in the "Radio Services Color Legend" of
https://www.ntia.gov/sites/default/files/publications/january_2016_spectrum_wall_chart_0.pdf
"""
import re

NTIA_COLORS = {
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
    "METEOROLOGICAL": "#efd7c2",
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

# Names used in bands.json that the chart's legend lists under another name.
ALIASES = {"METEOROLOGICAL AIDS": "METEOROLOGICAL"}


def services(text):
    """The NTIA services named in a bands.json `services` string, in order, without repeats.

    Qualifiers share the main service's color: '(R)', '(AIS)', '(space-to-Earth)',
    'except aeronautical mobile', '... uplinks in 401–403'. Lower-case names (secondary
    allocations, e.g. 'Amateur') get the same color as the primary name.
    """
    out = []
    for part in re.split(r"[;,]| and (?=[A-Z])", text):
        name = re.sub(r"\([^)]*\)", "", part)           # (R), (AIS), (space-to-Earth), ...
        name = re.split(r" except | uplinks", name)[0]  # 'MOBILE except ...', '... uplinks in ...'
        name = " ".join(name.upper().replace("-", " ").split())
        if not name:
            continue
        name = ALIASES.get(name, name)
        if name == "INTER SATELLITE":
            name = "INTER-SATELLITE"
        if name not in NTIA_COLORS:
            raise ValueError(f"no NTIA color for service {part.strip()!r} (read as {name!r})")
        if name not in out:
            out.append(name)
    return out
