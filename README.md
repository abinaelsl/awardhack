# awardhack

Answer one question, fast: **"I want to fly X→Y in cabin Z — which program should I burn, and
is it actually a good deal?"**

Built for a Fukuoka-based flyer sitting on KrisFlyer miles and a handful of transferable
currencies, whose real question is *"why do people online get 17,500-mile business seats when
I keep paying 57,000?"*

```
python3 -m awardhack route FUK CGK -c J --cash 95000
```

```
Fukuoka (FUK) → Jakarta (CGK)   Business
direct 3,155 mi (5,078 km) | itinerary flown 3,155 mi

CHARTS (what the program's published chart says you'd pay one-way)
    miles  program               basis                                        value
  ----------------------------------------------------------------------------------------
   30,000  ANA               [P] ANA zone 1A → 4: 60,000 RT / 2               3.17 ¥/mi* 🔥 banger
   40,000  JAL own           [P] JAL one-way base miles from Japan            2.38 ¥/mi* ✅ great
   48,000  JAL oneworld      [P] total itinerary 3,155 mi → band 1-4,000      1.98 ¥/mi* 😐 fair
   50,000  Turkish M&S       [s] Turkish zone 9 → zone 9 (all of East/SE Asia) 1.90 ¥/mi* 😐 fair
   52,500  KrisFlyer (Star)  [P] Star N_ASIA1 ⇄ SE_ASIA2: 105,000 RT / 2      1.81 ¥/mi* 😐 fair
   57,000  KrisFlyer (SQ)    [P] SQ zone 7 ⇄ zone 2                           1.67 ¥/mi* 😐 fair
   60,000  Asia Miles        [s] distance 3,155 mi → band 2,751-5,000         1.58 ¥/mi* 😐 fair
   62,000  Avios (QR)        [s] distance 3,155 mi → band 3,001-4,000         1.53 ¥/mi* 😐 fair
```

That is the whole product: **same seat, eight different prices**, plus a live cross-check of
what award space was actually observed on the route in the last 30 days.

## Why fixed charts still matter

Award pricing is not one thing. There are four mechanisms, and the gap between them on the same
route is routinely 2×:

| mechanism | examples | behaviour |
|---|---|---|
| zone matrix | KrisFlyer (SQ + Star), ANA, Asia Miles multi-carrier | fixed price per zone pair; the "chart" you memorise |
| distance bands | JAL oneworld, Avios, Asia Miles own-metal | price follows total miles flown, so the connection you take changes the price |
| same-zone flat | Turkish Miles&Smiles | all of East+SE Asia is Zone 9, so Japan→Indonesia prices like a domestic hop |
| dynamic | Flying Blue, LifeMiles, Aeroplan, United, Delta | price moves with cash fares and demand; often the cheapest and the only way to see 17k business |

The last row is why "just use KrisFlyer" loses. On BKK→CGK in business, the observed 30-day
best was **23,000 Flying Blue miles** while every fixed chart wanted 22,000–48,000.

## Install

No dependencies (Python 3.10+, stdlib only).

```bash
cd ~/award-hack
python3 -m awardhack route FUK CGK -c J --cash 95000
python3 tests.py            # 29 chart assertions
```

Optional entry point:

```bash
pip install --user .        # then just: awardhack route FUK CGK
```

## Commands

```
awardhack route ORIGIN DEST [-c Y|W|J|F] [--via HKG ...] [--cash N --cash-currency JPY]
                            [--no-live] [--refresh] [--json] [-v]
awardhack sweet             # curated sweet-spot library with the catch for each
awardhack transfers         # which card currency reaches which program
awardhack watch             # JSON digest of watchlist.json (for cron)
```

Useful flags:

- `--cash` — the fare you'd otherwise pay. The tool reports **¥ per mile** net of taxes, which
  is the only number that makes two programs comparable.
  `≥3.0 ¥/mi` = banger, `≥2.0` = great, `≥1.3` = fair, below that pay cash.
- `--via HKG` — prices the itinerary you'd actually fly, which matters for the distance-based
  charts (JAL oneworld, Avios, Asia Miles).
- `--no-live` — pure chart mode, no network.
- `--json` — machine-readable, for piping into a cron job or another agent.

Rule of thumb thresholds are stored in `awardhack/cli.py::VERDICTS`; change them if your
cash-fare baseline changes.

## Honesty about the data

Every number in `awardhack/data.py` carries:

- `source` — the URL it came from,
- `as_of` — the effective date of that chart,
- `confidence` — `primary` (transcribed from the airline's own chart/PDF) or `secondary`
  (reputable third-party chart; shortlist with it, confirm at booking).

What is **primary** here: KrisFlyer SQ Saver + Star partner PDFs (1 Nov 2025), JAL own-metal
one-way chart (Apr 2026) and JAL oneworld distance chart, ANA partner chart PDF.

What is **secondary**: Turkish partner charts, Qatar Avios distance chart, Asia Miles standard
chart. Fine for shortlisting, not for a transfer decision.

What is deliberately **absent**: Avianca LifeMiles, Aeroplan, United, Delta, Alaska and Flying
Blue are dynamic — publishing a chart for them would be a lie. The tool prices them only through
the live layer, which reads what was actually observed.

## The live layer

`awardhack/live.py` reads AwardTool's public per-route pages
(`awardtool.com/award-flights/{from}-{to}`), which publish the lowest award observed per program
in the last 30 days. No key, no login. 12-hour cache in `~/.cache/awardhack/`.

It is a cross-check, not the source of truth: it can only report programs with space in the last
30 days, and award space disappears. Never transfer points before searching the program itself.

## Known limits

- Chart rows transcribed: SQ Saver only for Zone 1 (Singapore) and Zone 2 (Malaysia/Indonesia/
  Brunei) — the two rows that price anything touching Indonesia. Others: read the PDF in `source`.
- ANA: the RT chart is transcribed; one-way prices are assumed to be ~half (ANA's one-way charts
  have existed since 24 Jun 2025). Confirm on ANA's calculator before transferring.
- KrisFlyer's Star zones publish "North Asia 1" and "North Asia 2" without a country list; both
  price 105,000 RT to SE Asia 2 so the mapping used here cannot change a Japan↔Indonesia price.
- Distances are great-circle. Real TPM (what charts actually use) runs 0–5% higher, which can
  flip a band edge. The tool prints raw distance so you can see when you're near an edge.
- Taxes/fuel surcharges are **not** in the static charts (they're unknown until you search).
  The value math flags this with `*`.

## Cron

`awardhack watch` prints a JSON digest of `watchlist.json` (cheapest chart price per route plus
the best awards actually observed in the last 30 days). Hermes runs it weekly as job
`awardhack-watch`, Mon 09:00 JST, delivering to DM.

The scheduler's script hook takes a **file path**, not a shell command, so the job points at
`~/AppData/Local/hermes/scripts/awardhack_watch.py`, which shells out to
`python3 -m awardhack watch` in the repo and prints its JSON.

## Layout

```
awardhack/airports.py    78 airports + haversine
awardhack/data.py        every chart, sweet spot and their sources
awardhack/engine.py      chart → miles, per program, with the derivation string
awardhack/live.py        AwardTool live cross-check + FX
awardhack/transfers.py   card currency → program map
awardhack/cli.py         the CLI
tests.py                 29 assertions, each traceable to a chart line
watchlist.json           routes worth re-checking on a schedule
docs/research-notes.md   the underlying research, with citations
```
