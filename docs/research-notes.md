# Spending miles optimally — research notes

Compiled 2026-10-28. Every number below is either transcribed from the airline's own published
chart (marked **[P]**) or from a reputable third-party chart/live observation (marked **[s]**).
Sources at the bottom.

---

## 1. The mistake: one program, one chart

You are not "booking with KrisFlyer miles". You are buying a seat with a **pricing mechanism**.
There are four, and on the same seat they differ by 2–3×:

| mechanism | who uses it | what it means for you |
|---|---|---|
| **Zone matrix** | KrisFlyer (SQ + Star), ANA, Asia Miles multi-carrier | one price per zone pair, ignores routing |
| **Distance bands** | JAL oneworld, Qatar/BA Avios, Asia Miles own-metal | price follows the miles you fly — the connection changes the price |
| **Flat same-zone** | Turkish Miles&Smiles | all of East + SE Asia is Zone 9, so Japan→Indonesia prices like a short hop |
| **Dynamic** | Flying Blue, LifeMiles, Aeroplan, United, Delta, Alaska | price tracks the cash fare; can be cheapest by far, and is where "17,500 business" screenshots come from |

Practical consequence: **your KrisFlyer balance is one of eight ways to buy the same seat**, and
KrisFlyer was the *worst or second-worst* option on four of five routes tested.

## 2. Japan → Jakarta, business, one-way — the actual spread **[P]**

| program | miles | derivation | ¥/mi at a ¥95,000 cash fare |
|---|---|---|---|
| ANA Mileage Club (partner award) | **30,000** | Japan 1-A → Asia 2: 60,000 round trip ÷ 2 | 3.17 🔥 |
| JAL Mileage Bank (own metal) | 40,000 | one-way base miles, Japan→Jakarta | 2.38 ✅ |
| JAL oneworld (distance) | 48,000 | itinerary 3,155 mi → band 1–4,000 | 1.98 |
| Turkish Miles&Smiles | 50,000 | Zone 9 → Zone 9 **[s]** | 1.90 |
| KrisFlyer on Star partners | 52,500 | North Asia ⇄ SE Asia 2: 105,000 RT ÷ 2 | 1.81 |
| **KrisFlyer on SQ metal** | **57,000** | SQ zone 7 ⇄ zone 2 | 1.67 |
| Asia Miles own-metal | 60,000 | 3,155 mi → band 2,751–5,000 **[s]** | 1.58 |
| Qatar Avios (distance) | 62,000 | 3,155 mi → band 3,001–4,000 **[s]** | 1.53 |
| *observed, 30 days to 26 Oct 2026* | 49,500 | FUK→CGK business, Air France/KLM Flying Blue + $175 | 1.36 net |

**Reading**: the seat costs 30,000 in ANA miles and 57,000 in KrisFlyer miles. Nearly 2×.
ANA is reachable from Amex Membership Rewards (Japan) at 1,000 pt : 1,000 mile.

## 3. Why the "banger" prices exist — the mechanism inventory

### (a) Same-zone flat pricing
Turkish treats **all** of Brunei, Cambodia, China, Hong Kong, Indonesia, Japan, Korea, Laos,
Macau, Malaysia, Philippines, Singapore, Taiwan, Thailand and Vietnam as **Zone 9**. A 3,000-mile
Japan→Indonesia flight prices the same as a 700-mile Bangkok→Kuala Lumpur one. **[s]**

### (b) Don't pay for the hub you don't want
KrisFlyer's Singapore↔Indonesia band is 22,000 in business **[P]** — an hour and a half in a
regional business seat for less than half of what the same program wants for SIN↔Bangkok
(25,000) or SIN↔Japan (54,500). Regional zones are where fixed charts are still generous.

### (c) Dynamic programs dip below every chart
BKK→CGK business, observed in the 30 days to 26 Oct 2026: **23,000 Flying Blue miles + $110
taxes** — below every fixed chart for that route (Avios 22,000, KrisFlyer SQ 26,500, Asia Miles
27,000, KrisFlyer Star 28,500, JAL oneworld 48,000). **[s]** Flying Blue and LifeMiles do this on
short intra-Asia segments regularly; the monthly Flying Blue "Promo Rewards" list adds 25–50% off
selected routes.

### (d) Distance bands reward short routings, punish them too
JAL oneworld prices on **total itinerary distance**, and allows one-way awards **[P]**. Adding a
connection can push you over a band edge: 4,000 mi and 4,001 mi are 48,000 vs 80,000 miles in
business. The same chart makes 1–4,000 mi business 48,000 and 8,001–10,000 mi business 85,000 —
so a well-routed Japan→SE Asia one-way sits in the cheapest band.

### (e) Fuel surcharge is half the price
Japan-origin tickets carry brutal YQ on JAL, ANA, SQ. Programs that largely don't pass partner
YQ — Avianca LifeMiles, Aeroplan, United, Alaska — can beat a "cheaper" chart once you add ¥15,000
–¥30,000 of surcharge. **Always compare net of taxes**, which is why the tool reports ¥/mi net.

### (f) One-way vs round-trip mechanics
ANA's partner chart is round-trip with one-way charts since 24 Jun 2025 **[P]**. JAL one-way is
permitted on oneworld awards **[P]**. KrisFlyer Star awards: one-way = exactly half the RT chart,
except itineraries with a stopover, which price per sector **[P]**. That last rule is a lever:
a stopover can be *cheaper* than a through-fare on some Star routings, and it also means you
should never buy a "round trip" when two one-ways price lower.

### (g) The transfer layer is where value leaks
Amex Membership Rewards (Japan) transfers at 1,000 : 1,000 to **13** airline programs, including
ANA, JAL and Flying Blue **[P — amex.co.jp]**. Transfers are not instant (days), and Bonvoy is
3:1 with a 5,000-mile bonus per 60,000 points. Never move points before a seat is held.
Indonesian bank cards mostly transfer to KrisFlyer only — that is the constraint that has been
forcing every decision into one program.

### (h) Method > memorised sweet spots
Nobody finds these by reading charts. The productive loop is: **search observed award prices on
the route first** (awardtool / seats.aero), see which programs actually have space and at what
price, then check whether you can fund that program. Reverse-engineering from "what does my
program charge" is how you end up paying 57,000 for a 30,000 seat.

## 4. What the 17,500 actually was

Verified on the charts: **17,500 is the Japan↔SE Asia *economy* price**, twice over —
ANA partner award NRT→CGK economy 35,000 RT ÷ 2 = 17,500 **[P]**, and KrisFlyer Star partner
NRT→CGK economy 35,000 RT ÷ 2 = 17,500 **[P]**. Business on those same charts is 30,000 and
52,500. So either the seat you saw was economy, or it was a dynamic program (Flying Blue /
LifeMiles) dipping below chart on a low-demand date. Both are real; the tool now tells them apart
because it prices both mechanisms.

## 5. Numbers worth memorising (Japan-based, verified **[P]**)

- JAL own-metal one-way business from Japan: Jakarta/Singapore/KL **40,000**, Bangkok 37,500–40,000,
  Manila 24,000, Hanoi/Saigon 30,000, Seoul 18,000, Honolulu 43,000, Europe 55,000–57,000,
  North America 55,000.
- JAL oneworld distance business: ≤4,000 mi **48,000**, 4,001–8,000 **80,000**,
  14,001–20,000 **120,000**, 20,001–25,000 **150,000**.
- ANA partner round trip business: Japan→Asia 2 **60,000**, →Hawaii 65,000, →North America 85,000,
  →Europe 90,000, Asia 2→Europe **136,000**.
- KrisFlyer SQ Saver one-way business: SIN↔Indonesia **22,000**, SIN↔Thailand 25,000,
  SIN↔Japan 54,500, Indonesia↔Japan **57,000**, SIN↔Europe 108,500.
- KrisFlyer Star partner RT business: SE Asia 2 ⇄ North Asia 105,000 (→52,500 one-way),
  SE Asia 2 within 57,000 (→28,500), Europe ⇄ North Asia 262,000.

## Sources

Primary (airline-published, transcribed into `awardhack/data.py`):

- KrisFlyer Singapore Airlines one-way Saver/Advantage chart, effective 1 Nov 2025 —
  `singaporeair.com/.../SingaporeAirlinesOne-WayAdvantageSaverAwardChartupdated1Nov25.pdf`
- KrisFlyer Star Alliance round-trip chart, effective 1 Nov 2025 —
  `singaporeair.com/.../StarAllianceRound-TripAwardChartupdated1Nov25.pdf`
- JAL International Award one-way chart, updated 16 Apr 2026 —
  `jal.co.jp/jp/en/jalmile/use/jal/inter/routemiles.html`
- JAL oneworld distance chart (Japan residents) — `jal.co.jp/jp/en/jalmile/use/partner_air/oneworld/miles.html`
- JAL oneway award conditions ("One-way trips are permitted") —
  `jal.co.jp/jp/en/jalmile/use/partner_air/oneworld/conditions.html`
- ANA partner airline award chart (RT, no seasonality) —
  `ana.co.jp/wws/japan/e/asw_common/amc/reference/tukau/award/tk/image/mileage_chart_en_tk.pdf`
- ANA partner zones (Asia 2 = Indonesia/Thailand/Singapore/…) —
  `ana.co.jp/en/jp/guide/amc/award/tk/zone/`
- Amex Japan Membership Rewards airline partners (13 programs, 1,000:1,000) —
  `americanexpress.com/ja-jp/point/mile-point/airline`

Secondary:

- Turkish Miles&Smiles partner zone chart — `10xtravel.com/turkish-airlines-award-charts`
- Qatar Privilege Club Avios distance chart — `10xtravel.com/qatar-airways-privilege-club-award-charts`
- Asia Miles standard + oneworld multi-carrier charts — `suitesmile.com/blog/2026/05/02/cathay-pacific-asia-miles-award-charts`
- Observed award prices per route/program (30-day window) — `awardtool.com/award-flights/{from}-{to}`
