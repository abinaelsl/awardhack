"""awardhack CLI — 'my route is X→Y, what is the best way to burn miles on it?'"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys

from . import airports as ap
from . import data, engine, live, transfers

WATCHLIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "watchlist.json")

CABIN_ALIASES = {"y": "Y", "economy": "Y", "w": "W", "pe": "W", "premium": "W",
                 "j": "J", "business": "J", "c": "J", "f": "F", "first": "F", "suite": "F"}

PROGRAM_TAG = {
    "krisflyer_sq": "KrisFlyer (SQ)", "krisflyer_star": "KrisFlyer (Star)",
    "jal_own": "JAL own", "jal_oneworld": "JAL oneworld", "ana_partner": "ANA",
    "turkish": "Turkish M&S", "avios": "Avios (QR)", "asiamiles": "Asia Miles",
}
PROGRAM_KEY = {v: k for k, v in PROGRAM_TAG.items()}

VERDICTS = [(3.0, "🔥 banger"), (2.0, "✅ great"), (1.3, "😐 fair"), (0.0, "💸 poor")]


def verdict(yen_per_mile: float) -> str:
    for floor, label in VERDICTS:
        if yen_per_mile >= floor:
            return label
    return "?"


def _cab(s: str) -> str:
    c = CABIN_ALIASES.get(s.lower())
    if not c:
        raise argparse.ArgumentTypeError(f"unknown cabin: {s}")
    return c


def _fmt_option_row(o: engine.Option, cash_jpy: float | None, usdjpy: float,
                    discount: float = 0.0) -> str:
    val = ""
    miles = int(round(o.miles * (1 - discount / 100.0))) if discount else o.miles
    if cash_jpy:
        ypm = cash_jpy / miles   # gross of taxes: chart rows carry unknown YQ
        val = f"{ypm:4.2f} ¥/mi* {verdict(ypm)}"
        if discount:
            val += f"  (−{discount:.0f}% → {miles:,})"
    tag = "P" if o.confidence == "primary" else "s"
    return (f"  {o.miles:>7,}  {PROGRAM_TAG.get(o.program, o.program):<17} [{tag}] "
            f"{o.basis:<44} {val}")


def cmd_route(args) -> int:
    o = args.origin.upper() if args.origin.upper() in ap.AIRPORTS else None
    if o is None:
        hits = ap.lookup(args.origin)
        if not hits:
            print(f"could not resolve airport: {args.origin}", file=sys.stderr)
            return 2
        o = hits[0]
    if args.destination.upper() in ap.AIRPORTS:
        d = args.destination.upper()
    else:
        hits = ap.lookup(args.destination)
        if not hits:
            print(f"could not resolve airport: {args.destination}", file=sys.stderr)
            return 2
        d = hits[0]
    via = args.via or []
    dist = engine.route_distance(o, d, via)
    cabin = args.cabin

    _real_stdout = sys.stdout
    if args.json:
        sys.stdout = io.StringIO()          # --json must emit JSON only, for piping

    print(f"\n{ap.name(o)} ({o}) → {ap.name(d)} ({d})   {engine.CABIN_NAMES[cabin]}"
          + (f"   via {'/'.join(via)}" if via else ""))
    print(f"direct {dist['direct_mi']:,} mi ({dist['direct_km']:,} km) | "
          f"itinerary flown {dist['itinerary_mi']:,} mi\n")

    usdjpy = args.usdjpy or live.fx_usdjpy()
    cash_jpy = None
    if args.cash:
        cash_jpy = args.cash * live.fx_rate((args.cash_currency or "JPY").upper(), "JPY")

    opts = engine.price_all(o, d, cabin, via)
    print("CHARTS (what the program's published chart says you'd pay one-way)")
    print(f"  {'miles':>7}  {'program':<17}     {'basis':<44} value")
    print("  " + "-" * 88)
    for opt in opts:
        print(_fmt_option_row(opt, cash_jpy, usdjpy, args.discount))
        for n in opt.notes[:1]:
            if args.verbose:
                print(f"           ↳ {n}")
    print("\n  [P] = transcribed from the airline's own chart   [s] = third-party chart, verify at booking")
    print("  * gross of taxes/YQ — subtract those before comparing to a cash fare")

    # transfer reachability
    print("\nCAN YOU ACTUALLY FUND IT")
    for opt in opts[:6]:
        keys = transfers.reachable(opt.program)
        print(f"  {PROGRAM_TAG.get(opt.program, opt.program):<17} ← "
              + (", ".join(transfers.TRANSFERS[k]["name"].split(" (")[0] for k in keys) or "no card route"))

    # live layer
    if not args.no_live:
        blob = live.fetch_route(o, d, ignore_cache=args.refresh)
        print("\nLIVE OBSERVED (AwardTool, last 30 days of award space)")
        if not blob.get("ok"):
            print(f"  no live data ({blob.get('error') or 'nothing observed'})")
        else:
            for cab in ("F", "J", "W", "Y"):
                for program, miles, tax in blob["observed"].get(cab, []):
                    ypm = ""
                    tax_jpy = tax * usdjpy
                    if cash_jpy and cab == cabin:
                        net = (cash_jpy - tax_jpy) / miles
                        ypm = (f"{net:4.2f} ¥/mi net  {verdict(net)}" if net > 0
                               else "taxes exceed the cash fare — pay cash")
                    elif cab != cabin:
                        ypm = "(different cabin — no value calc)"
                    print(f"  {engine.CABIN_NAMES[cab]:<16} {miles:>7,} + ${tax:>7,.2f} taxes "
                          f"(¥{tax_jpy:>7,.0f}) {program:<30} {ypm}")
            print(f"  source {blob['url']}  ({blob.get('fetched_at')})")
            if blob.get("coverage"):
                print(f"  coverage: {blob['coverage'][0]} of {blob['coverage'][1]} tracked programs "
                      f"had space on this route")

    if cash_jpy:
        print(f"\nCASH BENCHMARK ¥{cash_jpy:,.0f}  (USD/JPY {usdjpy:.1f})")
        best = opts[0] if opts else None
        if best:
            ypm = cash_jpy / best.miles
            print(f"  cheapest chart: {PROGRAM_TAG.get(best.program)} at {best.miles:,} miles "
                  f"→ ¥{ypm:.2f} per mile ({verdict(ypm)})")
            print("  rule of thumb: ¥1.3/mi = meh, ¥2/mi = good, ¥3+/mi = book it now")

    if args.json:
        sys.stdout = _real_stdout
        print(json.dumps({
            "route": f"{o}-{d}", "cabin": cabin, "distance_mi": dist, "usdjpy": usdjpy,
            "cash_jpy": cash_jpy,
            "charts": [{"program": x.program, "miles": x.miles, "basis": x.basis,
                        "confidence": x.confidence, "source": x.source,
                        "notes": x.notes} for x in opts],
            "live": blob or None,
        }, indent=2, ensure_ascii=False))
    return 0


def cmd_sweet(args) -> int:
    for s in data.SWEET_SPOTS:
        print(f"\n{s['title']}")
        print(f"  {s['route']}  ·  {engine.CABIN_NAMES.get(s['cabin'], s['cabin'])}  ·  {s['miles']}")
        print(f"  program: {PROGRAM_TAG.get(s['program'], s['program'])}")
        print(f"  why:     {s['why']}")
        print(f"  catch:   {s['catch']}")
    print("\nData version", data.DATA_VERSION,
          "· full charts: awardhack/data.py · verify every number at booking")
    return 0


def cmd_transfers(args) -> int:
    for k, v in transfers.TRANSFERS.items():
        print(f"\n{v['name']}")
        print(f"  ratio: {v['ratio']}")
        print(f"  reaches: {', '.join(PROGRAM_TAG.get(p, p) for p in v['reaches'])}")
        if v.get("confirmed_partners"):
            print(f"  confirmed partners: {', '.join(v['confirmed_partners'])}")
        print(f"  note: {v['notes']}")
        print(f"  source: {v['source']}")
    return 0


def cmd_watch(args) -> int:
    if not os.path.exists(WATCHLIST):
        print(f"no watchlist at {WATCHLIST}", file=sys.stderr)
        return 2
    wl = json.load(open(WATCHLIST, encoding="utf-8"))
    out = []
    for item in wl["routes"]:
        o, d = item["from"], item["to"]
        cabin = item.get("cabin", "J")
        opts = engine.price_all(o, d, cabin)
        best = opts[0] if opts else None
        blob = live.fetch_route(o, d)
        line = {"route": f"{o}-{d}", "cabin": cabin,
                "cheapest_chart": (f"{PROGRAM_TAG.get(best.program)} {best.miles:,}"
                                   if best else None)}
        if blob.get("ok"):
            obs = []
            for cab in ("J", "Y"):
                for program, miles, tax in blob["observed"].get(cab, []):
                    obs.append({"cabin": cab, "program": program, "miles": miles, "tax_usd": tax})
            line["live"] = obs
        out.append(line)
    print(json.dumps({"generated": data.DATA_VERSION, "routes": out}, indent=2, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="awardhack",
                                description="Best-value way to burn miles on a given route.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("route", help="price a route across every program we know")
    r.add_argument("origin")
    r.add_argument("destination")
    r.add_argument("-c", "--cabin", type=_cab, default="J")
    r.add_argument("--via", nargs="*", default=[], help="connection airports, e.g. --via HKG")
    r.add_argument("--cash", type=float, help="cash fare you would otherwise pay")
    r.add_argument("--discount", type=float, default=0.0,
                   help="percent off for a program-wide award sale, e.g. 30")
    r.add_argument("--cash-currency", default="JPY",
                   choices=["JPY", "USD", "IDR", "THB", "SGD", "EUR", "KRW"])
    r.add_argument("--usdjpy", type=float, default=None)
    r.add_argument("--no-live", action="store_true", help="skip the live AwardTool check")
    r.add_argument("--refresh", action="store_true", help="ignore the 12h cache")
    r.add_argument("--json", action="store_true")
    r.add_argument("-v", "--verbose", action="store_true")
    r.set_defaults(func=cmd_route)

    s = sub.add_parser("sweet", help="print the curated sweet-spot library")
    s.set_defaults(func=cmd_sweet)

    t = sub.add_parser("transfers", help="which card currency reaches which program")
    t.set_defaults(func=cmd_transfers)

    w = sub.add_parser("watch", help="machine-readable digest of watchlist.json (cron)")
    w.set_defaults(func=cmd_watch)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
