"""Sanity tests: every assertion below is traceable to a line in a published chart.

Run: python3 tests.py
"""

from awardhack import airports as ap, engine, data

FAILED = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f" (expected {want!r})"))
    if not ok:
        FAILED.append(label)


def check_range(label, got, lo, hi):
    ok = lo <= got <= hi
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got:,.0f}")
    if not ok:
        FAILED.append(label)


def price(program, o, d, cabin="J", dist=None):
    for opt in engine.price_all(o, d, cabin):
        if opt.program == program:
            return opt.miles
    return None


# ---- geography
check_range("FUK-CGK distance (mi)", ap.distance_mi("FUK", "CGK"), 3100, 3200)
check_range("NRT-CGK distance (mi)", ap.distance_mi("NRT", "CGK"), 3550, 3700)
check_range("BKK-CGK distance (mi)", ap.distance_mi("BKK", "CGK"), 1400, 1450)
check_range("SIN-CGK distance (mi)", ap.distance_mi("SIN", "CGK"), 540, 560)

# ---- KrisFlyer SQ Saver, Nov-2025 chart (Zone 1 row / Zone 2 row)
check("KrisFlyer SQ SIN-CGK J", price("krisflyer_sq", "SIN", "CGK"), 22000)
check("KrisFlyer SQ SIN-BKK J", price("krisflyer_sq", "SIN", "BKK"), 25000)
check("KrisFlyer SQ CGK-FUK J", price("krisflyer_sq", "CGK", "FUK"), 57000)
check("KrisFlyer SQ FUK-SIN J", price("krisflyer_sq", "FUK", "SIN"), 54500)
check("KrisFlyer SQ SIN-CGK F", price("krisflyer_sq", "SIN", "CGK", "F"), 32000)
check("KrisFlyer SQ SIN-CGK Y", price("krisflyer_sq", "SIN", "CGK", "Y"), 8000)

# ---- KrisFlyer Star partner chart (RT / 2)
check("KrisFlyer Star FUK-CGK J", price("krisflyer_star", "FUK", "CGK"), 52500)
check("KrisFlyer Star NRT-CGK Y (the 17,500 number)", price("krisflyer_star", "NRT", "CGK", "Y"), 17500)
check("KrisFlyer Star SIN-CGK J", price("krisflyer_star", "SIN", "CGK"), 26500)

# ---- JAL own metal (base miles, one-way, from Japan)
check("JAL own NRT-CGK J", price("jal_own", "NRT", "CGK"), 40000)
check("JAL own FUK-CGK J", price("jal_own", "FUK", "CGK"), 40000)
check("JAL own NRT-SIN J", price("jal_own", "NRT", "SIN"), 40000)
check("JAL own NRT-ICN J", price("jal_own", "NRT", "ICN"), 18000)
check("JAL own HND-LHR J", price("jal_own", "HND", "LHR"), 57000)

# ---- JAL oneworld distance scheme (one-way, total itinerary)
opt = engine._jal_oneworld(3155, "J")
check("JAL oneworld 3,155 mi J", opt.miles, 48000)
check("JAL oneworld 4,500 mi J", engine._jal_oneworld(4500, "J").miles, 80000)
check("JAL oneworld 9,000 mi J", engine._jal_oneworld(9000, "J").miles, 85000)
check("JAL oneworld 13,500 mi J", engine._jal_oneworld(13500, "J").miles, 115000)

# ---- ANA partner chart (RT / 2)
check("ANA partner FUK-CGK J", price("ana_partner", "FUK", "CGK"), 30000)
check("ANA partner NRT-CGK Y (the 17,500 number)", price("ana_partner", "NRT", "CGK", "Y"), 17500)
check("ANA partner HND-LHR J", price("ana_partner", "HND", "LHR"), 45000)

# ---- distance-band charts
check("Avios BKK-CGK J", price("avios", "BKK", "CGK"), 22000)
check("Asia Miles BKK-CGK J", price("asiamiles", "BKK", "CGK"), 27000)
check("Turkish FUK-CGK J", price("turkish", "FUK", "CGK"), 50000)

# ---- engine invariants
for route in [("FUK", "CGK"), ("BKK", "CGK"), ("SIN", "CGK"), ("HND", "LHR"), ("NRT", "DPS")]:
    opts = engine.price_all(route[0], route[1], "J")
    assert opts, f"no options for {route}"
    assert opts == sorted(opts, key=lambda x: x.miles), f"not sorted for {route}"
    assert all(o.confidence in ("primary", "secondary") for o in opts)
print(f"PASS  engine returns sorted, confidence-tagged options for 5 sample routes "
      f"({len(data.PROGRAMS)} programs, {len(ap.AIRPORTS)} airports)")

# ---- CLI: sale discounts apply to one program only, and re-rank
import contextlib, io, json
from awardhack import cli


def run_json(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(list(argv))
    return rc, json.loads(buf.getvalue())


rc, out = run_json("route", "FUK", "CGK", "--funded", "--no-live", "--json",
                   "--discount", "30", "--cash", "95000")
by = {c["program"]: c["miles"] for c in out["charts"]}
check("Escapes -30% hits SQ metal (57,000 → 39,900)", by["krisflyer_sq"], 39900)
check("Escapes leaves Star partners alone", by["krisflyer_star"], 52500)
check("discounted SQ now ranks first", out["charts"][0]["program"], "krisflyer_sq")
check("best_funded is the discounted SQ award", out["best_funded"]["miles"], 39900)
check("--json --no-live emits live: null", out["live"], None)
rc, out = run_json("route", "HND", "LHR", "--funded", "--no-live", "--json")
check("--funded --json still returns JSON", rc, 0)

print()
if FAILED:
    raise SystemExit(f"{len(FAILED)} FAILED: {FAILED}")
print("all assertions passed")
