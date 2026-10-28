"""awardhack CLI — 'my route is X→Y, what is the best way to burn miles on it?'"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from datetime import datetime, timezone

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
    "krisflyer_ga": "KrisFlyer (Garuda)", "garudamiles_ga": "GarudaMiles",
}
PROGRAM_KEY = {v: k for k, v in PROGRAM_TAG.items()}

VERDICTS = [(3.0, "🔥 banger"), (2.0, "✅ great"), (1.3, "😐 fair"), (0.0, "💸 poor")]


def verdict(yen_per_mile: float) -> str:
    for floor, label in VERDICTS:
        if yen_per_mile >= floor:
            return label
    return "?"


def _wrap(text: str, width: int) -> list[str]:
    import textwrap
    return textwrap.wrap(text, width=width) or [""]


def _cab(s: str) -> str:
    c = CABIN_ALIASES.get(s.lower())
    if not c:
        raise argparse.ArgumentTypeError(f"unknown cabin: {s}")
    return c


def effective_miles(o: engine.Option, discount: float, discount_program: str) -> int:
    """Miles after an award sale. A sale (e.g. Spontaneous Escapes) is one program's, not all."""
    if discount and o.program == discount_program:
        return int(round(o.miles * (1 - discount / 100.0)))
    return o.miles


def _fmt_option_row(o: engine.Option, cash_jpy: float | None, usdjpy: float,
                    discount: float = 0.0, discount_program: str = "krisflyer_sq") -> str:
    val = ""
    miles = effective_miles(o, discount, discount_program)
    discount = discount if miles != o.miles else 0.0
    if cash_jpy:
        ypm = cash_jpy / miles   # gross of taxes: chart rows carry unknown YQ
        val = f"{ypm:4.2f} ¥/mi* {verdict(ypm)}"
        if discount:
            val += f"  (−{discount:.0f}% → {miles:,})"
    tag = "P" if o.confidence == "primary" else "s"
    return (f"  {o.miles:>7,}  {PROGRAM_TAG.get(o.program, o.program):<17} [{tag}] "
            f"{o.basis:<44} {val}")


def _chart_json(x: engine.Option, cash_jpy: float | None, miles: int) -> dict:
    """One chart row for --json / watch: everything an agent needs to rank and explain it."""
    ypm = round(cash_jpy / miles, 2) if cash_jpy else None
    return {"program": x.program, "label": PROGRAM_TAG.get(x.program, x.program),
            "miles": miles, "chart_miles": x.miles, "basis": x.basis,
            "confidence": x.confidence, "funded_from": transfers.mine(x.program),
            "yen_per_mile_gross": ypm, "verdict": verdict(ypm) if ypm else None,
            "source": x.source, "notes": x.notes}


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

    eff = lambda x: effective_miles(x, args.discount, args.discount_program)
    opts = sorted(engine.price_all(o, d, cabin, via), key=eff)
    dropped = []
    if args.funded:
        dropped = [x for x in opts if not transfers.mine(x.program)]
        opts = [x for x in opts if transfers.mine(x.program)]
        if not opts:
            if args.json:
                sys.stdout = _real_stdout
                print(json.dumps({"route": f"{o}-{d}", "cabin": cabin, "charts": [],
                                  "error": "no chart option reachable from your current cards"}))
                return 1
            print("\nNo chart option is reachable from your current cards on this route.")
            print("Run without --funded to see what you would need to open/fund.")
            return 1
    print("CHARTS (what the program's published chart says you'd pay one-way)")
    print(f"  {'miles':>7}  {'program':<17}     {'basis':<44} value")
    print("  " + "-" * 88)
    for opt in opts:
        print(_fmt_option_row(opt, cash_jpy, usdjpy, args.discount, args.discount_program))
        for n in opt.notes[:1]:
            if args.verbose:
                print(f"           ↳ {n}")
    print("\n  [P] = transcribed from the airline's own chart   [s] = third-party chart, verify at booking")
    print("  * gross of taxes/YQ — subtract those before comparing to a cash fare")

    # transfer reachability
    print("\nCAN YOU ACTUALLY FUND IT")
    for opt in opts[:6]:
        keys = transfers.reachable(opt.program)
        _mine = transfers.mine(opt.program)
        mark = "✅ TODAY" if _mine else "⛔ needs a new account"
        print(f"  {PROGRAM_TAG.get(opt.program, opt.program):<17} ← {mark}: "
              + (", ".join(transfers.TRANSFERS[k]["name"].split(" (")[0] for k in keys) or "no card route"))
    if dropped:
        print(f"  ({len(dropped)} option(s) hidden by --funded: "
              + ", ".join(PROGRAM_TAG.get(x.program, x.program) for x in dropped) + ")")

    # live layer
    blob = None
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
            ypm = cash_jpy / eff(best)
            print(f"  cheapest chart: {PROGRAM_TAG.get(best.program)} at {eff(best):,} miles "
                  f"→ ¥{ypm:.2f} per mile ({verdict(ypm)})")
            print("  rule of thumb: ¥1.3/mi = meh, ¥2/mi = good, ¥3+/mi = book it now")

    if args.json:
        sys.stdout = _real_stdout
        print(json.dumps({
            "route": f"{o}-{d}", "cabin": cabin, "distance_mi": dist, "usdjpy": usdjpy,
            "cash_jpy": cash_jpy,
            "charts": [_chart_json(x, cash_jpy, eff(x)) for x in opts],
            "best_funded": next((_chart_json(x, cash_jpy, eff(x)) for x in opts
                                 if transfers.mine(x.program)), None),
            "live": blob,
        }, indent=2, ensure_ascii=False))
    return 0


def cmd_sweet(args) -> int:
    for s in data.SWEET_SPOTS:
        print(f"\n{s['title']}")
        print(f"  {s['route']}  ·  {engine.CABIN_NAMES.get(s['cabin'], s['cabin'])}  ·  {s['miles']}")
        print(f"  program: {PROGRAM_TAG.get(s['program'], s['program'])}")
        print(f"  why:     {s['why']}")
        print(f"  catch:   {s['catch']}")
    print("\nHARD RULES (no routing trick beats these)")
    for title, body, src in transfers.HARD_RULES:
        print(f"\n  {title}")
        for line in _wrap(body, 92):
            print(f"    {line}")
        print(f"    src: {src}")
    print("\nData version", data.DATA_VERSION,
          "· full charts: awardhack/data.py · verify every number at booking")
    return 0


def cmd_cards(args) -> int:
    idr = live.fx_rate("IDR", "JPY")
    print("\nCARD SHORTLIST  (per-mile cost at the realistic tier; lower is better)")
    for market in ("Japan", "Indonesia"):
        print(f"\n  ── {market}-issued " + "─" * 60)
        for card in data.CARDS:
            if card["market"] != market:
                continue
            pm = card["per_mile"]
            if "JPY" in pm:
                cost = f"¥{pm['JPY']:,}/mile"
            else:
                cost = f"Rp{pm['IDR']:,}/mile  (¥{pm['IDR'] * idr:,.0f})"
            print(f"\n  {card['name']}")
            print(f"    fee   {card['annual_fee']:<28} {cost}")
            print(f"    reaches {', '.join(PROGRAM_TAG.get(x, x) for x in card['reach'])}")
            for line in _wrap(card["why"], 88):
                print(f"    + {line}")
            for line in _wrap(card["catch"], 88):
                print(f"    ! {line}")
    print("\n  rule: earn rate decides the card, transfer partners decide the program. "
          "A card that cannot reach ANA is worth nothing for a 30,000-mile ANA seat.")
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


# AwardTool program names → our program keys (only the ones his cards can reach matter)
LIVE_NAME_KEYS = {"krisflyer": "krisflyer_sq", "garuda": "garudamiles_ga"}


def _is_funded_live(name: str) -> bool:
    n = name.lower()
    return any(k in n and transfers.mine(p) for k, p in LIVE_NAME_KEYS.items())


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
        funded = next((x for x in opts if transfers.mine(x.program)), None)
        blob = live.fetch_route(o, d)
        line = {"route": f"{o}-{d}", "cabin": cabin, "note": item.get("note"),
                "cheapest_chart": (f"{PROGRAM_TAG.get(best.program)} {best.miles:,}"
                                   if best else None),
                "cheapest_funded_chart": (f"{PROGRAM_TAG.get(funded.program)} {funded.miles:,}"
                                          if funded else None)}
        if blob.get("ok"):
            # watched cabin first, then the others for context
            obs = [{"cabin": cab, "program": program, "miles": miles, "tax_usd": tax}
                   for cab in [cabin] + [c for c in ("F", "J", "W", "Y") if c != cabin]
                   for program, miles, tax in blob["observed"].get(cab, [])]
            line["live"] = obs
            same = [x for x in obs if x["cabin"] == cabin]
            # actionable: space seen in a program his cards can actually reach
            line["bookable_now"] = [x for x in same if _is_funded_live(x["program"])]
            if same and funded and min(x["miles"] for x in same) < funded.miles:
                low = min(same, key=lambda x: x["miles"])
                line["cheaper_elsewhere"] = (f"{low['program']} seen at {low['miles']:,} vs "
                                             f"{funded.miles:,} fundable today")
        else:
            line["live_error"] = blob.get("error") or "nothing observed"
        out.append(line)
    print(json.dumps({"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                      "data_version": data.DATA_VERSION, "funded_from": transfers.MY_CURRENCIES,
                      "routes": out}, indent=2, ensure_ascii=False))
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
    r.add_argument("--funded", action="store_true",
                   help="only show programs you can fund from the card currencies you actually hold")
    r.add_argument("--discount", type=float, default=0.0,
                   help="percent off for a program-wide award sale, e.g. 30")
    r.add_argument("--discount-program", default="krisflyer_sq", choices=sorted(PROGRAM_TAG),
                   help="which program the sale applies to (default: KrisFlyer SQ metal, "
                        "i.e. Spontaneous Escapes)")
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

    c = sub.add_parser("cards", help="card shortlist ranked by rupiah/yen per mile")
    c.set_defaults(func=cmd_cards)

    w = sub.add_parser("watch", help="machine-readable digest of watchlist.json (cron)")
    w.set_defaults(func=cmd_watch)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
