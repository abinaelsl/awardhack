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


def cmd_capacity(args) -> int:
    """Where the next rupiah of credit limit should go. Capacity, not rate, is the constraint."""
    path = args.file or os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "limits.json")
    blob = json.load(open(path, encoding="utf-8"))
    cycles = float(blob.get("cycles_per_year", 12.0))
    mile_idr = float(blob.get("mile_value_idr", 200))
    cards = {x["id"]: x for x in data.CARDS}
    rows = []
    for entry in blob["cards"]:
        meta = cards.get(entry["card"])
        if not meta:
            continue
        per_mile = meta["per_mile"].get("IDR")
        if not per_mile:
            continue
        limit = entry.get("limit", 0)
        spend = limit * cycles
        miles = spend / per_mile
        value = miles * mile_idr
        net = value - entry.get("annual_fee", 0)
        rows.append({"name": meta["name"], "limit": limit, "per_mile": per_mile,
                     "spend": spend, "miles": miles, "value": value,
                     "fee": entry.get("annual_fee", 0), "net": net,
                     "per_limit_jt": (1_000_000 * cycles / per_mile) * mile_idr})
    rows.sort(key=lambda r: -r["limit"])
    print(f"\nCAPACITY VIEW  ({cycles:.1f} cycles/yr, mile valued at Rp{mile_idr:,.0f})")
    print(f"  {'card':<34}{'limit':>13}{'Rp/mile':>10}{'miles/yr':>11}{'value/yr':>13}{'net of AF':>13}")
    print("  " + "-" * 93)
    tot_miles = tot_net = tot_limit = 0
    for r in rows:
        print(f"  {r['name'][:33]:<34}{r['limit']:>13,.0f}{r['per_mile']:>10,.0f}"
              f"{r['miles']:>11,.0f}{r['value']:>13,.0f}{r['net']:>13,.0f}")
        tot_miles += r["miles"]; tot_net += r["net"]; tot_limit += r["limit"]
    print("  " + "-" * 93)
    print(f"  {'TOTAL':<34}{tot_limit:>13,.0f}{'':>10}{tot_miles:>11,.0f}{'':>13}{tot_net:>13,.0f}")

    print("\n  MARGINAL: what one more Rp1,000,000 of limit is worth per year")
    for r in sorted(rows, key=lambda r: -r["per_limit_jt"]):
        print(f"    {r['name'][:33]:<34} Rp{r['per_limit_jt']:>9,.0f}/yr  "
              f"(earn rate Rp{r['per_mile']:,.0f}/mile)")
    print("\n  Reading: a limit INCREASE on a good-rate card is free money — no new annual fee,")
    print("  no new application. Only add a new card when the increases stall; then rank the")
    print("  candidates by marginal miles, and check the annual fee against the limit it unlocks.")
    return 0


def cmd_float(args) -> int:
    """Credit-limit leverage math. Miles are the side-effect, not the point."""
    limit = args.limit
    cyc = max(1, args.cycle_days)
    cycles = 365.0 / cyc
    net = (args.margin - args.fx) / 100.0          # net margin per cycle
    ann = (1 + net) ** cycles - 1
    simple = net * cycles
    fee_drag = (args.annual_fee / limit) if limit else 0.0
    usdjpy = live.fx_usdjpy()
    idr = live.fx_rate("IDR", "JPY")

    print(f"\nCREDIT-FLOAT MODEL  limit {limit:,.0f} {args.currency}  "
          f"cycle {cyc}d  margin {args.margin}%/cycle  fx drag {args.fx}%/cycle")
    print(f"  cycles per year        {cycles:>8.1f}")
    print(f"  net margin per cycle   {net*100:>8.2f}%")
    print(f"  annualised (compounded){ann*100:>8.1f}%")
    print(f"  annualised (simple)    {simple*100:>8.1f}%")
    if fee_drag:
        print(f"  annual fee drag        {fee_drag*100:>8.2f}% of limit "
              f"({args.annual_fee:,.0f} {args.currency}/yr)")
    print(f"  gross profit / year    {(1+net)**cycles*limit - limit:>14,.0f} {args.currency}")

    if args.per_mile:
        spend_yr = limit * cycles
        miles = spend_yr / args.per_mile
        gravy_native = miles * args.mile_value_jpy
        # convert gravy into the limit currency to compare like for like
        if args.currency.upper() == "IDR":
            gravy_ccy = gravy_native / idr
        else:
            gravy_ccy = gravy_native
        print(f"\n  MILES AS GRAVY")
        print(f"    spend throughput     {spend_yr:>14,.0f} {args.currency}/yr")
        print(f"    earn rate            {args.per_mile:,.0f} {args.currency}/mile")
        print(f"    miles per year       {miles:>14,.0f}")
        profit = (1 + net) ** cycles * limit - limit
        print(f"    gravy value          {gravy_ccy:>14,.0f} {args.currency} "
              f"(¥{gravy_native:,.0f})")
        print(f"    gravy % of spend     {gravy_ccy/spend_yr*100:>7.2f}% per year")
        print(f"    gravy % of limit     {gravy_ccy/limit*100:>7.2f}% per year")
        print(f"    gravy vs margin      {gravy_ccy/profit*100:>7.0f}% of the arbitrage "
              f"profit — at this turnover miles are NOT gravy, they are a margin line")

    print("\n  BREAK-EVEN NOTES")
    print(f"    a {args.annual_fee:,.0f} {args.currency} annual fee needs "
          f"{args.annual_fee/limit*100:.2f}% of limit in margin just to cancel out")
    print(f"    every 1.0% of extra FX drag costs {limit*0.01*cycles:,.0f} {args.currency}/yr "
          f"at this turnover")
    print("    the edge dies instantly if you ever carry a balance "
          "(ID cards ~2%/month, JP cards ~15%/yr) — full payment, every cycle")
    print("\n  not advice, and not a licence to kite: paying one card with another is a "
          "closure event at every issuer in both countries.")
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

    cap = sub.add_parser("capacity", help="where the next rupiah of credit limit should go")
    cap.add_argument("--file", help="path to limits.json (default: repo root)")
    cap.set_defaults(func=cmd_capacity)

    fl = sub.add_parser("float", help="credit-limit leverage math (float, not miles)")
    fl.add_argument("--limit", type=float, required=True, help="total credit limit")
    fl.add_argument("--currency", default="IDR", choices=["IDR", "JPY", "USD"])
    fl.add_argument("--margin", type=float, default=2.0, help="gross %% per cycle")
    fl.add_argument("--fx", type=float, default=0.0, help="FX/other drag %% per cycle")
    fl.add_argument("--cycle-days", type=int, default=30)
    fl.add_argument("--annual-fee", type=float, default=0.0)
    fl.add_argument("--per-mile", type=float, default=0.0,
                    help="native currency spent per mile (e.g. 16667 IDR)")
    fl.add_argument("--mile-value-jpy", type=float, default=1.8)
    fl.set_defaults(func=cmd_float)

    w = sub.add_parser("watch", help="machine-readable digest of watchlist.json (cron)")
    w.set_defaults(func=cmd_watch)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
