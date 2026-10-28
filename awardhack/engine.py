"""Chart engine: turn (program, origin, destination, cabin) into a mileage price."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import airports as ap
from . import data

CABINS = ("Y", "W", "J", "F")
CABIN_NAMES = {"Y": "Economy", "W": "Premium Economy", "J": "Business", "F": "First"}


@dataclass
class Option:
    program: str
    label: str
    miles: int
    cabin: str
    basis: str                      # how the number was derived
    confidence: str                 # primary | secondary
    notes: list[str] = field(default_factory=list)
    source: str = ""
    taxes_note: str = "taxes/YQ extra"
    distance_mi: float | None = None


def _find_zone(scheme: dict, code: str):
    code = code.upper()
    for zone, members in scheme.items():
        if code in members:
            return zone
    return None


# ----------------------------------------------------------------------- SQ
def _krisflyer_sq(origin: str, dest: str, cabin: str) -> Option | None:
    prog = data.PROGRAMS["krisflyer_sq"]
    zo = _find_zone(data.SQ_ZONES, origin)
    zd = _find_zone(data.SQ_ZONES, dest)
    if zo is None or zd is None:
        return None
    matrix = prog["matrix"]
    row = matrix.get(zo) or matrix.get(zd)
    if row is None:
        return Option("krisflyer_sq", prog["name"], 0, cabin,
                      basis=f"zone {zo}->{zd}: row not transcribed",
                      confidence=prog["confidence"],
                      notes=["Only SQ Zone 1 and Zone 2 rows are transcribed. "
                             "Open the Saver PDF in the source field."],
                      source=prog["source"])
    col = zd if (matrix.get(zo) is not None) else zo
    miles = row.get(cabin, {}).get(col)
    if miles is None:
        return None
    return Option("krisflyer_sq", prog["name"], miles, cabin,
                  basis=f"SQ zone {zo} ⇄ zone {zd}", confidence=prog["confidence"],
                  notes=[prog["notes"]], source=prog["source"])


# ------------------------------------------------------------ Star partners
def _krisflyer_star(origin: str, dest: str, cabin: str) -> Option | None:
    prog = data.PROGRAMS["krisflyer_star"]
    zo = _find_zone(data.STAR_ZONES, origin)
    zd = _find_zone(data.STAR_ZONES, dest)
    if zo is None or zd is None or cabin not in ("Y", "J", "F"):
        return None
    order = prog["region_matrix"]["order"]
    if zo not in order or zd not in order:
        return None
    vals = prog["region_matrix"]["values"][zo][order.index(zd)]
    rt = vals[("Y", "J", "F").index(cabin)]
    return Option("krisflyer_star", prog["name"], rt // 2, cabin,
                  basis=f"Star {zo} ⇄ {zd}: {rt:,} RT / 2",
                  confidence=prog["confidence"], notes=[prog["notes"]],
                  source=prog["source"])


# ------------------------------------------------------------------ JAL own
def _jal_own(origin: str, dest: str, cabin: str) -> Option | None:
    prog = data.PROGRAMS["jal_own"]
    o, d = origin.upper(), dest.upper()
    if ap.region(o) != "JAPAN":
        return None
    row = prog["city_table"].get(d)
    if row is None:
        return None
    miles = row[("Y", "W", "J").index("Y" if cabin == "Y" else "W" if cabin == "W" else "J")]
    if miles is None:
        return None
    return Option("jal_own", prog["name"], miles, cabin,
                  basis="JAL one-way base miles from Japan", confidence=prog["confidence"],
                  notes=[prog["notes"]], source=prog["source"])


# ------------------------------------------------------ JAL oneworld distance
def _jal_oneworld(total_mi: float, cabin: str) -> Option | None:
    prog = data.PROGRAMS["jal_oneworld"]
    if cabin not in ("Y", "J", "F"):
        return None
    for lo, hi, vals in prog["bands"]:
        if lo <= total_mi <= hi:
            miles = vals[("Y", "J", "F").index(cabin)]
            return Option("jal_oneworld", prog["name"], miles, cabin,
                          basis=f"total itinerary {total_mi:,.0f} mi → band {lo:,}-{hi:,}",
                          confidence=prog["confidence"], notes=[prog["notes"]],
                          source=prog["source"], distance_mi=total_mi)
    return None


# ------------------------------------------------------------- ANA partner
def _ana_partner(origin: str, dest: str, cabin: str) -> Option | None:
    prog = data.PROGRAMS["ana_partner"]
    if cabin not in ("Y", "J", "F"):
        return None
    zo = data.ANA_ZONE_MAP.get(ap.region(origin))
    zd = data.ANA_ZONE_MAP.get(ap.region(dest))
    if not zo or not zd:
        return None
    table = prog["region_matrix"]["values"]
    row = key = None
    if zo.startswith("1") and zd not in table.get(zo, {}):
        # Japan origin, zone key not spelled the same way → fall back to the 1-A row
        if zd in table.get("1A", {}):
            row, key = table["1A"], "1A"
    elif zo in table and zd in table[zo]:
        row, key = table[zo], zo
    if row is None and zd.startswith("1") and zo in table.get("1A", {}):
        row, key = table["1A"], "1A"          # Indonesia → Japan prices symmetrically
    if row is None and zd in table and zo in table[zd]:
        row, key = table[zd], zd
    if row is None:
        return None
    col = zd if zo.startswith("1") else (zo if zd.startswith("1") else zd)
    if col not in row:
        return None
    rt = row[col][("Y", "J", "F").index(cabin)]
    return Option("ana_partner", prog["name"], rt // 2, cabin,
                  basis=f"ANA zone {key} → {zd}: {rt:,} RT / 2",
                  confidence=prog["confidence"],
                  notes=["One-way charts exist since Jun-2025 at ~half the RT chart; "
                         "confirm on ANA's calculator before transferring."],
                  source=prog["source"])


# ---------------------------------------------------------------- Turkish
def _turkish(origin: str, dest: str, cabin: str) -> Option | None:
    prog = data.PROGRAMS["turkish"]
    zo = _find_zone(data.TK_ZONES, origin)
    zd = _find_zone(data.TK_ZONES, dest)
    if zo is None or zd is None or zo != zd or cabin not in ("Y", "J", "F"):
        return None
    miles = prog["same_zone_prices"][zo][cabin]
    return Option("turkish", prog["name"], miles, cabin,
                  basis=f"Turkish zone {zo} → zone {zo} (all of East/SE Asia)",
                  confidence=prog["confidence"], notes=[prog["notes"]],
                  source=prog["source"])


# ------------------------------------------------------- distance-band charts
def _band_price(bands, dist_mi: float, cabin: str, program_key: str) -> Option | None:
    prog = data.PROGRAMS[program_key]
    idx = {"avios": {"Y": 0, "W": 1, "J": 2, "F": 3},
           "asiamiles": {"Y": 0, "W": 1, "J": 2, "F": 3}}[program_key]
    if cabin not in idx:
        return None
    for lo, hi, vals in bands:
        if lo <= dist_mi <= hi:
            miles = vals[idx[cabin]]
            if miles is None:
                return None
            return Option(program_key, prog["name"], miles, cabin,
                          basis=f"distance {dist_mi:,.0f} mi → band {lo:,}-{hi:,}",
                          confidence=prog["confidence"], notes=[prog["notes"]],
                          source=prog["source"], distance_mi=dist_mi)
    return None


# --------------------------------------------------------------------- API
def price_all(origin: str, destination: str, cabin: str = "J",
              via: list[str] | None = None) -> list[Option]:
    """Every program we have a chart for, priced for this route."""
    o, d = origin.upper(), destination.upper()
    for c in (o, d):
        if c not in ap.AIRPORTS:
            raise KeyError(f"unknown airport code: {c}")
    cabin = cabin.upper()
    via = [v.upper() for v in (via or [])]

    direct_mi = ap.distance_mi(o, d)
    legs = [o] + via + [d]
    total_mi = sum(ap.distance_mi(legs[i], legs[i + 1]) for i in range(len(legs) - 1))

    opts: list[Option] = []
    for fn in (_krisflyer_sq(o, d, cabin), _krisflyer_star(o, d, cabin),
               _jal_own(o, d, cabin), _ana_partner(o, d, cabin), _turkish(o, d, cabin)):
        if fn:
            opts.append(fn)

    # distance-based programs: price the itinerary actually flown
    for key in ("jal_oneworld", "avios", "asiamiles"):
        if key == "jal_oneworld":
            opt = _jal_oneworld(total_mi, cabin)
        else:
            prog = data.PROGRAMS[key]
            opt = _band_price(prog["bands"], total_mi, cabin, key)
        if opt:
            opts.append(opt)

    opts = [x for x in opts if x.miles]
    opts.sort(key=lambda x: x.miles)
    return opts


def route_distance(origin: str, destination: str, via: list[str] | None = None) -> dict:
    o, d = origin.upper(), destination.upper()
    via = [v.upper() for v in (via or [])]
    legs = [o] + via + [d]
    direct = ap.distance_mi(o, d)
    total = sum(ap.distance_mi(legs[i], legs[i + 1]) for i in range(len(legs) - 1))
    return {"direct_mi": round(direct), "direct_km": round(ap.distance_km(o, d)),
            "itinerary_mi": round(total), "legs": legs}
