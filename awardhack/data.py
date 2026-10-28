"""
Award-chart data, transcribed from the issuing program's own published chart.

Every block carries:
  source        - the primary URL the numbers came from
  as_of         - effective date of that chart
  confidence    - "primary"   = transcribed from the airline's own chart / PDF
                  "secondary" = transcribed from a reputable third-party chart
                                (use it to shortlist, then confirm at booking)

Numbers are ONE-WAY POINTS PER PERSON unless the block says round_trip=True.
"""

from __future__ import annotations

DATA_VERSION = "2026-10-28"

# ---------------------------------------------------------------- SQ own zones
# KrisFlyer zone numbers used by the Singapore Airlines Saver/Advantage charts.
SQ_ZONES = {
    1: ["SIN"],
    2: ["KUL", "BKI", "BWN", "CGK", "DPS", "SUB", "MES", "PLM", "SRG", "UPG"],
    3: ["BKK", "DMK", "HKT", "CNX", "SGN", "HAN", "DAD", "MNL", "CEB", "PNH", "RGN", "VTE", "REP"],
    4: ["HKG", "MFM", "TPE", "CAN", "SZX", "XMN", "CTU", "CKG", "KMG"],
    5: ["PVG", "SHA", "PEK", "PKX", "TSN", "DLC", "SHE", "HGH", "WUH", "XIY", "CSX"],
    6: ["DEL", "BOM", "BLR", "MAA", "CMB", "MLE", "KTM", "DAC", "HYD", "AMD", "COK"],
    7: ["FUK", "NRT", "HND", "KIX", "ITM", "NGO", "CTS", "OKA", "HIJ", "ICN", "GMP", "PUS"],
    8: ["PER", "DRW"],
    9: ["SYD", "MEL", "BNE", "ADL", "AKL", "CHC"],
    10: ["DXB", "DOH", "AUH", "IST", "CAI", "JNB", "CPT", "MRU", "MLE"],
    11: ["LHR", "CDG", "FRA", "MUC", "AMS", "ZRH", "FCO", "HEL", "BCN", "MXP"],
    12: ["LAX", "SFO", "SEA", "YVR", "HNL"],
    13: ["JFK", "EWR", "ORD", "BOS", "IAD", "DFW", "IAH"],
}

# KrisFlyer Star Alliance partner zones (SQ's own grouping, 11 zones).
STAR_ZONES = {
    "SE_ASIA1": ["SIN", "KUL", "BWN", "BKI"],
    "SE_ASIA2": ["CGK", "DPS", "SUB", "BKK", "DMK", "HKT", "CNX", "SGN", "HAN", "DAD",
                 "MNL", "CEB", "PNH", "RGN", "VTE"],
    # NOTE: SQ publishes "North Asia 1" and "North Asia 2"; Japan's exact bucket is not
    # spelled out in the PDF and the two rows price 105,000 RT to SE Asia 2 either way,
    # so both Japan and Greater China/Korea are mapped to N_ASIA1. Difference only shows
    # on SE_ASIA1 (102,000 vs 105,000) and Europe (262,000 vs 275,000).
    "N_ASIA1": ["FUK", "NRT", "HND", "KIX", "ITM", "NGO", "CTS", "OKA", "HIJ",
                "ICN", "GMP", "PUS", "HKG", "MFM", "TPE", "PVG", "SHA", "PEK",
                "PKX", "CAN", "SZX", "CTU", "XIY"],
    "C_S_ASIA": ["DEL", "BOM", "BLR", "MAA", "CMB", "MLE", "KTM", "DAC", "HYD", "COK"],
    "SW_PACIFIC": ["SYD", "MEL", "BNE", "PER", "ADL", "AKL", "CHC", "GUM"],
    "ME_NA": ["DXB", "DOH", "AUH", "CAI", "JNB", "CPT"],
    "EUROPE": ["LHR", "CDG", "FRA", "MUC", "AMS", "ZRH", "FCO", "HEL", "IST"],
    "N_AMERICA": ["JFK", "EWR", "ORD", "BOS", "IAD", "DFW", "IAH", "LAX", "SFO",
                  "SEA", "YVR", "HNL"],
}

PROGRAMS = {}

# ---------------------------------------------------------------------------
# 1. KrisFlyer — Singapore Airlines metal, SAVER (one-way)
# ---------------------------------------------------------------------------
PROGRAMS["krisflyer_sq"] = {
    "name": "KrisFlyer — SQ metal, Saver",
    "short": "KrisFlyer (SQ)",
    "currency": "KrisFlyer miles",
    "round_trip": False,
    "type": "zone_matrix",
    "zone_map": "SQ",
    "alliance": "Star Alliance",
    "books": "singaporeair.com",
    "source": "https://www.singaporeair.com/content/dam/sia/web-assets/pdfs/ppsclub-krisflyer/krisflyer/progupdates/awardcharts/SingaporeAirlinesOne-WayAdvantageSaverAwardChartupdated1Nov25.pdf",
    "as_of": "2025-11-01",
    "confidence": "primary",
    # rows transcribed from the Nov-2025 Saver chart (thousands of miles)
    # row 1 = SIN, row 2 = Malaysia/Indonesia/Brunei
    "matrix": {
        1: {"Y": {2: 8000, 3: 13000, 4: 15500, 5: 20500, 6: 19000, 7: 25500, 8: 20500,
                  9: 29000, 10: 32000, 11: 44000, 12: 44000, 13: 46000},
            "W": {4: 28000, 5: 36000, 6: 36000, 7: 39500, 9: 53500, 10: 51500,
                  11: 74500, 12: 79000, 13: 84500},
            "J": {2: 22000, 3: 25000, 4: 35500, 5: 45000, 6: 45000, 7: 54500, 8: 42500,
                  9: 72000, 10: 68000, 11: 108500, 12: 112500, 13: 117000},
            "F": {2: 32000, 3: 38000, 4: 47500, 5: 61500, 6: 61500, 7: 81000, 8: 60500,
                  9: 98000, 10: 95000, 11: 148000, 12: 154000, 13: 156000}},
        2: {"Y": {1: 8000, 2: 8500, 3: 13500, 4: 16000, 5: 21000, 6: 20000, 7: 27000,
                  8: 21500, 9: 30500, 10: 33500, 11: 46000, 12: 46000, 13: 48500},
            "W": {4: 28500, 5: 37500, 6: 38000, 7: 41500, 9: 56000, 10: 54000,
                  11: 78000, 12: 82500, 13: 88500},
            "J": {1: 22000, 2: 23000, 3: 26500, 4: 36500, 5: 46500, 6: 47500, 7: 57000,
                  8: 44500, 9: 75500, 10: 70500, 11: 114000, 12: 117500, 13: 122500},
            "F": {1: 32000, 2: 33500, 3: 39500, 4: 48500, 5: 63000, 6: 64500, 7: 84500,
                  8: 63500, 9: 103000, 10: 99500, 11: 155000, 12: 161000, 13: 163500}},
    },
    "notes": "Only SQ's Zone 1 (Singapore) and Zone 2 (Malaysia/Indonesia/Brunei) rows are "
             "transcribed here — those are the two that price any itinerary touching "
             "Indonesia or Singapore. Everything else: read the PDF in `source`.",
}

# ---------------------------------------------------------------------------
# 2. KrisFlyer — Star Alliance partners (round-trip chart, one-way = half)
# ---------------------------------------------------------------------------
_STAR_ORDER = ["SE_ASIA1", "SE_ASIA2", "N_ASIA1", "C_S_ASIA", "SW_PACIFIC",
               "ME_NA", "EUROPE", "N_AMERICA"]
_STAR_RT = {
    "SE_ASIA1": [(18000, 47000, 68000), (29000, 53000, 80000), (35000, 102000, 126000),
                 (57000, 115000, 162000), (74000, 180000, 238000), (86000, 181000, 231000),
                 (104000, 228000, 349000), (128000, 262000, 369000)],
    "SE_ASIA2": [(29000, 53000, 80000), (29000, 57000, 84000), (35000, 105000, 132000),
                 (57000, 115000, 162000), (74000, 180000, 238000), (86000, 181000, 231000),
                 (104000, 228000, 349000), (128000, 262000, 369000)],
    "N_ASIA1": [(35000, 102000, 126000), (35000, 105000, 132000), (29000, 64000, 84000),
                (69000, 132000, 196000), (80000, 180000, 226000), (101000, 208000, 292000),
                (116000, 262000, 403000), (112000, 285000, 347000)],
    "C_S_ASIA": [(57000, 115000, 162000), (57000, 115000, 162000), (69000, 132000, 196000),
                 (29000, 64000, 84000), (102000, 242000, 285000), (88000, 172000, 198000),
                 (65000, 136000, 240000), (128000, 303000, 396000)],
    "SW_PACIFIC": [(74000, 180000, 238000), (74000, 180000, 238000), (80000, 180000, 226000),
                   (102000, 242000, 285000), (29000, 76000, 104000), (126000, 264000, 340000),
                   (133000, 292000, 404000), (139000, 323000, 415000)],
    "ME_NA": [(86000, 181000, 231000), (86000, 181000, 231000), (101000, 208000, 292000),
              (88000, 172000, 198000), (126000, 264000, 340000), (51000, 108000, 161000),
              (44000, 74000, 175000), (120000, 229000, 274000)],
    "EUROPE": [(104000, 228000, 349000), (104000, 228000, 349000), (116000, 262000, 403000),
               (65000, 136000, 240000), (133000, 292000, 404000), (44000, 74000, 175000),
               (30000, 76000, 106000), (65000, 179000, 267000)],
    "N_AMERICA": [(128000, 262000, 369000), (128000, 262000, 369000), (112000, 285000, 347000),
                  (128000, 303000, 396000), (139000, 323000, 415000), (120000, 229000, 274000),
                  (65000, 179000, 267000), (30000, 58000, 86000)],
}
PROGRAMS["krisflyer_star"] = {
    "name": "KrisFlyer — Star Alliance partner award",
    "short": "KrisFlyer (Star)",
    "currency": "KrisFlyer miles",
    "round_trip": True,          # chart is RT; one-way = half
    "type": "region_matrix",
    "zone_map": "STAR",
    "alliance": "Star Alliance",
    "books": "singaporeair.com (some partners need the reservation form / phone)",
    "source": "https://www.singaporeair.com/content/dam/sia/web-assets/pdfs/ppsclub-krisflyer/krisflyer/progupdates/awardcharts/StarAllianceRound-TripAwardChartupdated1Nov25.pdf",
    "as_of": "2025-11-01",
    "confidence": "primary",
    "region_matrix": {"order": _STAR_ORDER, "values": _STAR_RT, "cabins": ["Y", "J", "F"]},
    "notes": "One-way = half the chart. A one-way Star award containing a stopover is "
             "priced per sector instead. Fuel surcharges pass through on most partners.",
}

# ---------------------------------------------------------------------------
# 3. JAL Mileage Bank — JAL metal international award (one-way base miles)
# ---------------------------------------------------------------------------
JAL_OWN = {
    # dest: (Y, W, J) one-way base miles from Japan
    "CGK": (15000, 25000, 40000), "SIN": (13000, 25000, 40000),
    "KUL": (15000, 25000, 40000), "BKK": (13500, 25000, 40000),
    "HAN": (13000, 20000, 30000), "SGN": (13000, 20000, 30000),
    "MNL": (10000, 15000, 24000), "DEL": (17500, 25000, 40000),
    "BLR": (17500, 25000, 40000), "ICN": (7500, 15000, 18000),
    "GMP": (7500, 15000, 18000), "TPE": (9000, 15000, 24000),
    "HKG": (11000, None, 26000), "GUM": (10000, None, 23000),
    "HNL": (20000, 30000, 43000), "SYD": (23000, 31000, 45000),
    "MEL": (25000, 35000, 45000), "DOH": (20000, 30000, 50000),
    "LHR": (27000, 40000, 57000), "CDG": (27000, 40000, 57000),
    "FRA": (23000, 38000, 55000), "HEL": (23000, 38000, 55000),
    "JFK": (27000, 40000, 55000), "LAX": (27000, 40000, 55000),
    "SFO": (27000, 40000, 55000), "SEA": (27000, 40000, 55000),
    "ORD": (27000, 40000, 55000), "YVR": (27000, 40000, 55000),
}
PROGRAMS["jal_own"] = {
    "name": "JAL Mileage Bank — JAL metal international award",
    "short": "JAL (own metal)",
    "currency": "JAL miles",
    "round_trip": False,
    "type": "city_table",
    "alliance": "oneworld",
    "books": "jal.co.jp (base miles; Award Ticket PLUS costs extra)",
    "source": "https://www.jal.co.jp/jp/en/jalmile/use/jal/inter/routemiles.html",
    "as_of": "2026-04-16",
    "confidence": "primary",
    "city_table": JAL_OWN,
    "airline": "JL",
    "notes": "Base miles, one-way, from/to Japan. Fare class seasonality only affects First "
             "Class here; economy/PE/business base levels are flat. Fuel surcharge extra.",
}

# ---------------------------------------------------------------------------
# 4. JAL Mileage Bank — oneworld / partner award (distance scheme, one-way OK)
# ---------------------------------------------------------------------------
JAL_OW_BANDS = [
    (1, 4000, (25000, 48000, 72000)),
    (4001, 8000, (40000, 80000, 100000)),
    (8001, 10000, (50000, 85000, 110000)),
    (10001, 12000, (60000, 110000, 160000)),
    (12001, 14000, (70000, 115000, 165000)),
    (14001, 20000, (90000, 120000, 170000)),
    (20001, 25000, (120000, 150000, 230000)),
    (25001, 29000, (140000, 190000, 280000)),
    (29001, 34000, (150000, 200000, 300000)),
    (34001, 50000, (160000, 220000, 330000)),
]
PROGRAMS["jal_oneworld"] = {
    "name": "JAL Mileage Bank — oneworld award (distance scheme)",
    "short": "JAL (oneworld)",
    "currency": "JAL miles",
    "round_trip": False,
    "type": "distance_bands",
    "alliance": "oneworld",
    "books": "jal.co.jp",
    "source": "https://www.jal.co.jp/jp/en/jalmile/use/partner_air/oneworld/miles.html",
    "as_of": "2026-10-28",
    "confidence": "primary",
    "bands": JAL_OW_BANDS,
    "notes": "Priced on TOTAL itinerary distance (sum of sectors), so a connection can push "
             "you into a dearer band. One-way trips are expressly permitted. "
             "No First Class on Malaysia Airlines; 2-class AA/Alaska flights price as business.",
}

# ---------------------------------------------------------------------------
# 5. ANA Mileage Club — partner award (round-trip chart; one-way = half)
# ---------------------------------------------------------------------------
_ANA_ZONES = {
    "1A": "Japan", "1B": "Japan", "2": "South Korea / Russia-1",
    "3": "Asia 1 (CN/TW/HK/MO/PH/GUM)", "4": "Asia 2 (ID/TH/SG/MY/VN/IN...)",
    "5": "Hawaii", "6": "North America", "7": "Europe / Russia-2",
    "8": "Africa / Middle East", "9": "Central & South America", "10": "Oceania / Micronesia",
}
ANA_ZONE_MAP = {
    "JAPAN": "1A",
    "N_ASIA2": "2",   # Korea
    "N_ASIA1": "3",   # Greater China, Philippines, Guam
    "SE_ASIA1": "4", "SE_ASIA2": "4", "S_ASIA": "4",
    "HAWAII": "5", "N_AMERICA": "6", "EUROPE": "7",
    "MIDDLE_EAST": "8", "AFRICA": "8", "S_AMERICA": "9", "SW_PACIFIC": "10",
}
# row zone -> {col zone: (Y, C, F)} round-trip
ANA_RT = {
    "1A": {"2": (15000, 30000, 45000), "3": (20000, 40000, 60000), "4": (35000, 60000, 105000),
           "5": (40000, 65000, 120000), "6": (50000, 85000, 150000), "7": (55000, 90000, 165000),
           "9": (45000, 75000, 135000)},
    "1B": {"2": (18000, 33000, 54000), "3": (23000, 43000, 69000), "4": (38000, 63000, 114000),
           "5": (43000, 68000, 129000), "6": (55000, 90000, 165000), "7": (60000, 95000, 180000),
           "8": (70000, 110000, 210000), "9": (90000, 143000, 270000), "10": (50000, 80000, 150000)},
    "4": {"5": (30000, 55000, 90000), "6": (65000, 105000, 195000), "7": (80000, 136000, 240000),
          "8": (59000, 94000, 177000), "9": (50000, 80000, 150000), "10": (105000, 168000, 315000)},
}
PROGRAMS["ana_partner"] = {
    "name": "ANA Mileage Club — partner airline award",
    "short": "ANA (partner)",
    "currency": "ANA miles",
    "round_trip": True,          # one-way charts exist since 2025-06-24 at ~half
    "type": "region_matrix_rt",
    "zone_map": "ANA",
    "alliance": "Star Alliance",
    "books": "ana.co.jp",
    "source": "https://www.ana.co.jp/wws/japan/e/asw_common/amc/reference/tukau/award/tk/image/mileage_chart_en_tk.pdf",
    "as_of": "2026-10-28",
    "confidence": "primary",
    "region_matrix": {"values": ANA_RT, "cabins": ["Y", "J", "F"]},
    "notes": "Round-trip chart, no seasonality (partner chart). One-way charts exist for "
             "tickets issued on/after 2025-06-24 and price at about half. Zone 1-A = a plain "
             "international round trip; 1-B = anything more complicated (more expensive).",
}

# ---------------------------------------------------------------------------
# 6. Turkish Miles&Smiles — Star partner award (one-way)
# ---------------------------------------------------------------------------
TK_ZONES = {
    "9": ["FUK", "NRT", "HND", "KIX", "ITM", "NGO", "CTS", "OKA", "ICN", "GMP", "PUS",
          "HKG", "MFM", "TPE", "PVG", "SHA", "PEK", "PKX", "CAN", "SZX", "CTU",
          "CGK", "DPS", "SUB", "BKK", "DMK", "HKT", "CNX", "SGN", "HAN", "DAD",
          "MNL", "CEB", "PNH", "RGN", "VTE", "KUL", "BWN", "SIN", "DEL", "BOM", "BLR", "MAA"],
}
PROGRAMS["turkish"] = {
    "name": "Turkish Airlines Miles&Smiles — partner award",
    "short": "Turkish M&S",
    "currency": "Miles&Smiles miles",
    "round_trip": False,
    "type": "zone_matrix_same",
    "alliance": "Star Alliance",
    "books": "turkishairlines.com",
    "source": "https://10xtravel.com/turkish-airlines-award-charts",
    "as_of": "2026-10-28",
    "confidence": "secondary",
    "same_zone_prices": {"9": {"Y": 35000, "J": 50000, "F": 75000}},
    "notes": "Turkish lumps all of East/SE Asia into Zone 9, so Japan↔Indonesia prices like a "
             "domestic hop — but 50,000 J one-way is still not cheap. Miles are hard to get "
             "from Japanese cards; usually bought (frequent 100%+ bonus sales).",
}

# ---------------------------------------------------------------------------
# 7. Qatar Privilege Club / Avios — distance-based (one-way)
# ---------------------------------------------------------------------------
AVIOS_BANDS = [
    (1, 650, (6000, 9000, 12500, 24000)),
    (651, 1151, (9000, 12500, 16500, 33000)),
    (1152, 2000, (11000, 16500, 22000, 44000)),
    (2001, 3000, (13000, 25250, 38750, 51500)),
    (3001, 4000, (20750, 41250, 62000, 82500)),
    (4001, 5500, (25750, 51500, 77250, 103000)),
    (5501, 6500, (31000, 62000, 92750, 123750)),
    (6501, 7000, (36250, 72250, 108250, 144250)),
    (7001, 99999, (51500, 103000, 154500, 206000)),
]
PROGRAMS["avios"] = {
    "name": "Avios — Qatar Privilege Club distance chart (Qatar metal)",
    "short": "Avios (QR)",
    "currency": "Avios",
    "round_trip": False,
    "type": "distance_bands",
    "alliance": "oneworld",
    "books": "qatarairways.com",
    "source": "https://10xtravel.com/qatar-airways-privilege-club-award-charts",
    "as_of": "2026-10-28",
    "confidence": "secondary",
    "bands": AVIOS_BANDS,
    "notes": "Per-sector distance bands. Qatar metal only for these rates; British Airways "
             "and Iberia run their own Avios charts. Great for short 1-2 sector hops.",
}

# ---------------------------------------------------------------------------
# 8. Cathay / Asia Miles — own-flight Standard chart (one-way, distance bands)
# ---------------------------------------------------------------------------
CX_STANDARD = [
    (1, 750, (7000, 11000, 16000, None)),
    (751, 2750, (9000, 18000, 27000, 43000)),   # Type 1
    (2751, 5000, (20000, 39000, 60000, 90000)),
    (5001, 7500, (27000, 52000, 91000, 125000)),
    (7501, 99999, (38000, 78000, 119000, 160000)),
]
CX_MULTICARRIER = [
    (1, 1000, (30000, 60000, 75000)),
    (1001, 1500, (35000, 65000, 85000)),
    (1501, 2000, (40000, 70000, 95000)),
    (2001, 4000, (45000, 80000, 110000)),
    (4001, 7500, (63000, 100000, 150000)),
    (7501, 9000, (68000, 120000, 165000)),
    (9001, 10000, (77000, 135000, 175000)),
    (10001, 14000, (95000, 170000, 250000)),
    (14001, 18000, (105000, 210000, 310000)),
    (18001, 20000, (115000, 230000, 330000)),
    (20001, 25000, (126000, 250000, 350000)),
    (25001, 35000, (140000, 265000, 365000)),
    (35001, 50000, (160000, 280000, 380000)),
]
PROGRAMS["asiamiles"] = {
    "name": "Cathay Pacific Asia Miles — own-flight Standard chart",
    "short": "Asia Miles (CX)",
    "currency": "Asia Miles",
    "round_trip": False,
    "type": "distance_bands",
    "alliance": "oneworld",
    "books": "cathaypacific.com",
    "source": "https://suitesmile.com/blog/2026/05/02/cathay-pacific-asia-miles-award-charts",
    "as_of": "2026-05-02",
    "confidence": "secondary",
    "bands": CX_STANDARD,
    "alt_bands": {"oneworld_multicarrier": CX_MULTICARRIER},
    "notes": "Own-flight Standard = the level that matters; Choice/Tailored cost more. "
             "Multi-carrier oneworld itineraries use a much dearer distance chart "
             "(see alt_bands) — that is why CX via HKG to Jakarta prices badly.",
}

# ---------------------------------------------------------------------------
# Curated sweet-spot library (each one traceable to a source above)
# ---------------------------------------------------------------------------
SWEET_SPOTS = [
    {
        "id": "krf-sin-id",
        "title": "Singapore ↔ Indonesia, SQ metal, Saver",
        "route": "SIN ⇄ CGK/DPS/SUB",
        "cabin": "J",
        "miles": "22,000 J one-way / 32,000 First",
        "program": "krisflyer_sq",
        "why": "The classic regional red-eye bargain — 1.5h flight at long-haul-grade seat "
               "for a fraction of the 46,500 it costs to fly SIN↔BKK in J.",
        "catch": "Saver availability on SIN-CGK is thin at peak; Advantage costs 46,000 J.",
    },
    {
        "id": "jal-id",
        "title": "Japan → Jakarta, JAL metal, base miles",
        "route": "NRT/HND/KIX → CGK",
        "cabin": "J",
        "miles": "40,000 J one-way (15,000 Y)",
        "program": "jal_own",
        "why": "Fixed, season-free business pricing on JAL's own chart, and the only way to "
               "reach Jakarta nonstop-ish from Japan in J without a Star partner surcharge.",
        "catch": "Fuel surcharge is chunky on JAL tickets issued in Japan; Award Ticket PLUS "
                 "can push the price up when only expensive inventory is left.",
    },
    {
        "id": "ana-partner-id",
        "title": "Japan ⇄ Southeast Asia, ANA partner award",
        "route": "Japan ⇄ Asia 2 (ID/TH/SG/MY/VN)",
        "cabin": "J",
        "miles": "60,000 J round-trip ⇒ ~30,000 one-way",
        "program": "ana_partner",
        "why": "Cheapest per-direction partner pricing into Indonesia that we could verify. "
               "Use it on Thai via BKK, SQ via SIN, or ANA metal.",
        "catch": "Round-trip chart; one-way tables (post Jun-2025) run ~half. Confirm the "
                 "one-way number on ANA's own calculator before transferring.",
    },
    {
        "id": "krf-star-half",
        "title": "Any Star Alliance carrier, via KrisFlyer",
        "route": "e.g. Japan ⇄ Indonesia",
        "cabin": "J",
        "miles": "105,000 J round-trip ⇒ 52,500 one-way",
        "program": "krisflyer_star",
        "why": "KrisFlyer can book every Star carrier, not just SQ — the escape hatch when "
               "SQ itself has no Saver space.",
        "catch": "Worst value of the Star options on intra-Asia. Never worth it if you can "
                 "reach the same seat with ANA miles instead.",
    },
    {
        "id": "avios-short",
        "title": "1–2 hour hops for pocket change with Avios",
        "route": "under 2,000 mi per sector",
        "cabin": "J",
        "miles": "12,500 (≤650mi) / 16,500 (651–1,151mi) / 22,000 (1,152–2,000mi) Avios",
        "program": "avios",
        "why": "Per-sector distance pricing means BKK↔KUL, KUL↔CGK, HKG↔TPE style hops are "
               "absurdly cheap in business — this is where '17,500 business' stories come from.",
        "catch": "Priced per sector, so a connection doubles it. Qatar metal only for the "
                 "published QR bands; BA/Iberia differ.",
    },
    {
        "id": "jal-ow-distance",
        "title": "Round-the-region one-way under 4,000 mi with oneworld",
        "route": "total itinerary distance ≤ 4,000 mi",
        "cabin": "J",
        "miles": "48,000 J one-way / 25,000 Y",
        "program": "jal_oneworld",
        "why": "One-way is expressly allowed, and 8 sectors per award means multi-city "
               "Asia trips (Japan → HKG → BKK → CGK) can hide inside one band.",
        "catch": "Total distance includes every sector, so a detour can jump you to 80,000. "
                 "One surface sector allowed; no stopover inside Japan on Japan-origin awards.",
    },
    {
        "id": "cx-standard",
        "title": "Cathay own-metal regional business",
        "route": "≤2,750 mi per one-way",
        "cabin": "J",
        "miles": "27,000 Asia Miles (751–2,750 mi Type 1)",
        "program": "asiamiles",
        "why": "Japan↔HK, HK↔BKK, HK↔CGK on Cathay metal stays in the cheap band.",
        "catch": "Routing Japan→Jakarta via HKG blows past the band and drops you on the "
                 "multi-carrier chart (60,000+). Only good for single-sector-ish trips.",
    },
    {
        "id": "krf-zone-addon",
        "title": "KrisFlyer zone pricing: the Singapore stop is almost free",
        "route": "FUK/NRT → SIN → CGK on SQ metal",
        "cabin": "J",
        "miles": "57,000 total (FUK→SIN alone is 54,500)",
        "program": "krisflyer_sq",
        "why": "SQ prices the ZONE PAIR, not the segments: Japan zone 7 → Indonesia zone 2 is "
               "57,000 J whether you fly one sector or two. Adding Singapore costs 2,500 miles — "
               "a second destination for ~4% more.",
        "catch": "Stopover (not just transit) rules differ: a Saver one-way generally cannot "
                 "hold a stopover; price it as two awards (54,500 + 22,000) if you want to stay "
                 "in Singapore. Transit-only still gets the 57,000 price.",
    },
    {
        "id": "krf-star-cheaper",
        "title": "Same balance, different chart: Star partners beat SQ metal",
        "route": "Japan ⇄ Indonesia",
        "cabin": "J",
        "miles": "52,500 (Star partner) vs 57,000 (SQ metal)",
        "program": "krisflyer_star",
        "why": "KrisFlyer miles on ANA/Thai/EVA metal price off the Star Alliance chart "
               "(North Asia ⇄ SE Asia 2 = 105,000 RT ÷ 2), which is 4,500 miles cheaper than "
               "SQ's own zone chart for the identical trip.",
        "catch": "Star partners pass fuel surcharges; on a Japan-origin ticket that can be "
                 "¥15,000-30,000. Compare net, and remember a one-way WITH a stopover prices "
                 "per sector.",
    },
    {
        "id": "krf-escapes",
        "title": "Spontaneous Escapes: 30% off SQ metal, monthly",
        "route": "whatever SQ lists that month",
        "cabin": "J",
        "miles": "e.g. SIN→CGK J 22,000 → 15,400; Japan↔Indonesia 57,000 → 39,900",
        "program": "krisflyer_sq",
        "why": "SQ discounts selected Saver awards ~30% for travel in the following month. It is "
               "the single biggest lever available to a KrisFlyer-only wallet — 39,900 for "
               "Japan→Jakarta business beats the ANA chart that is otherwise out of reach.",
        "catch": "Travel window is one month, blackout/route lists change monthly, and Japan "
                 "routes are not always included. Book within the promo window; run "
                 "`--discount 30` to price it.",
    },
    {
        "id": "ga-kf",
        "title": "Garuda Indonesia, booked with KrisFlyer (bilateral, not Star)",
        "route": "SIN ⇄ CGK/SUB 24,000 · SIN ⇄ DPS 21,000 · CGK ⇄ DPS 21,000",
        "cabin": "J",
        "miles": "21,000–24,000 J one-way (economy 13,500)",
        "program": "krisflyer_ga",
        "why": "GA joined KrisFlyer for redemptions in Aug 2025, so SQ miles now book Garuda's "
               "nonstops — including CGK↔DPS, where 21,000 undercuts SQ's own 23,000 "
               "within-zone price.",
        "catch": "Only the listed city pairs are on the chart (Singapore/Denpasar/Jakarta/"
                 "Surabaya/Lombok/Labuan Bajo/Sam Ratulangi). Garuda's Japan flights are NOT "
                 "bookable with KrisFlyer miles — for those you would need GarudaMiles. "
                 "UNVERIFIED: not transcribed from SQ's partner chart, and third-party reports "
                 "conflict (one gives a flat 13,500 Y / 24,000 J on every SIN pair). Check "
                 "singaporeair.com before relying on the 21,000 prices.",
    },
]

# ---------------------------------------------------------------------------
# Card shortlist for Abinael's two spend jurisdictions, verified 2026-10-28.
# "per_mile" = native currency spent per 1 airline mile, at the card's realistic
# earning tier (not the headline teaser rate). Lower is better.
# ---------------------------------------------------------------------------
CARDS = [
    # ---- Japan-issued: where he actually spends (JPY) ----
    {
        "id": "ana_student_jcb",
        "name": "ANAカード (学生用) JCB",
        "market": "Japan",
        "annual_fee": "free while enrolled",
        "per_mile": {"JPY": 100},
        "reach": ["ana_partner"],
        "why": "200円 = 2 ANA miles (1.0%), plus 1,000 bonus miles every year and "
               "1 mile per 100-200円 at ANA Card Mile Plus shops. The ANA JCB is the "
               "only version at the double rate — VISA/Mastercard are 0.5%.",
        "catch": "Needs Japanese residence + student status (confirm 研究生 counts). "
                 "Locks you into ANA miles, which is exactly what unlocks the 30,000 "
                 "Japan→Indonesia business price and ANA's nonstop NH855 HND→CGK.",
        "source": "https://www.ana.co.jp/ja/jp/amc/anacard/st_card",
    },
    {
        "id": "jal_navi",
        "name": "JALカード navi (student)",
        "market": "Japan",
        "annual_fee": "free while enrolled",
        "per_mile": {"JPY": 100},
        "reach": ["jal_own", "jal_oneworld"],
        "why": "Shopping miles double during enrollment (≈100円 = 1 mile), miles DO NOT "
               "EXPIRE while you are a student, and navi holders get JAL's discounted "
               "award rates — which matters because JAL's own chart already prices "
               "Japan→Jakarta J at 40,000.",
        "catch": "Rebuilds the JAL account he lost. JAL miles are still the least "
                 "flexible of his options; treat it as the backup to ANA.",
        "source": "https://www.jal.co.jp/jp/ja/jalcard/card/navi.html",
    },
    {
        "id": "amex_jp_mr",
        "name": "Amex Membership Rewards (Japan) — Green/Gold",
        "market": "Japan",
        "annual_fee": "¥13,200 (Green) / ¥31,900 (Gold)",
        "per_mile": {"JPY": 100},
        "reach": ["ana_partner", "krisflyer_sq", "krisflyer_star", "asiamiles", "avios",
                  "jal_own", "jal_oneworld"],
        "why": "13 airline partners at 1,000 points = 1,000 miles. The only card in his "
               "reach that can pivot between ANA, KrisFlyer, Asia Miles and Avios after "
               "the fact — flexibility is worth paying an annual fee for.",
        "catch": "JAL transfer ratio is poor (skip that path). ANA transfers cost a "
                 "¥5,500/yr course fee. Transfers take days, never do it before you hold "
                 "a seat.",
        "source": "https://www.americanexpress.com/ja-jp/point/mile-point/airline",
    },
    {
        "id": "bonvoy_amex_jp",
        "name": "Marriott Bonvoy Amex (Japan)",
        "market": "Japan",
        "annual_fee": "¥16,500 (varies)",
        "per_mile": {"JPY": 240},
        "reach": ["ana_partner", "jal_own", "krisflyer_sq", "turkish", "asiamiles"],
        "why": "Bonvoy 3:1 (60,000 → 25,000 miles) reaches 40+ airlines including ANA and "
               "JAL — the widest net available from Japan.",
        "catch": "¥240 per mile is 2.4x worse than the ANA card. Use Bonvoy for hotel "
                 "stays and only convert when a bonus or a specific seat justifies it.",
        "source": "https://www.marriott.com/loyalty/redeem/travel/points-to-miles.mi",
    },
    # ---- Indonesia-issued: where the rupiah spends ----
    {
        "id": "dbs_vantage_id",
        "name": "DBS Indonesia Vantage (or digibank MC)",
        "market": "Indonesia",
        "annual_fee": "Rp4-5,000,000 (NOT waivable on Vantage)",
        "per_mile": {"IDR": 7500},
        "reach": ["krisflyer_sq", "krisflyer_star"],
        "why": "Rp7,500 per KrisFlyer mile (10,000 Vantage Points = 10,000 miles), the best "
               "per-mile rate of any card he actually holds. Points never expire.",
        "catch": "Earning is capped at 1x credit limit per month, and the Vantage annual fee "
                 "(Rp4-5jt, non-waivable) is larger than a year of miles at low turnover — the "
                 "fee, not the rate, decides whether this card nets positive.",
        "source": "https://pinterpoin.com/review-kartu-kredit-dbs-vantage-visa-infinite",
    },
    {
        "id": "jenius_cc",
        "name": "Kartu Kredit Jenius (BTPN)",
        "market": "Indonesia",
        "annual_fee": "low",
        "per_mile": {"IDR": 6667},
        "reach": ["krisflyer_sq", "krisflyer_star", "garudamiles"],
        "why": "Rp6,667 per KrisFlyer mile on Double Yay categories, and up to 60,000 "
               "KrisFlyer miles/month at Bloom tier. He ALREADY HOLDS THIS — it is 2.5x "
               "better per mile than the Danamon JCB Precious.",
        "catch": "Only 1 conversion per airline per month (40,000 Yay → 30,000 KF at "
                 "Grow/Nurture/Bloom; 50,000 Yay at Seed/Plant).",
        "source": "https://pinterpoin.com/10-kartu-kredit-terbaik-krisflyer-miles",
    },
    {
        "id": "danamon_jcb_precious",
        "name": "Danamon JCB Precious",
        "market": "Indonesia",
        "annual_fee": "Rp800,000 (waivable)",
        "per_mile": {"IDR": 16667},
        "reach": ["krisflyer_sq", "asiamiles", "garudamiles", "jal_own"],
        "why": "Six airline partners from a mid-tier card (GarudaMiles 15 D-Point = 1 mile, "
               "KrisFlyer/Asia Miles 20 = 1, JAL 32 = 1) and genuinely useful Japan perks: "
               "unlimited domestic ID lounges, 6x/yr JCB lounges in Japan & Hawaii, "
               "8x/yr LoungeKey, and JCB acceptance everywhere in Japan.",
        "catch": "Rp16,667 per KrisFlyer mile even at the best tier — the WORST miles rate "
                 "of any card on this list. The ≥Rp50,000,000 placement only buys the 3.0 "
                 "vs 2.5 D-Point tier (+20% points) plus the AF waiver. Buy this card for "
                 "lounges and JCB coverage, never for the miles rate.",
        "source": "https://pinterpoin.com/review-kartu-kredit-danamon-jcb-precious",
    },
    {
        "id": "mandiri_prioritas",
        "name": "Mandiri Prioritas World MC",
        "market": "Indonesia",
        "annual_fee": "free at Prioritas",
        "per_mile": {"IDR": 6667},
        "reach": ["krisflyer_sq", "krisflyer_star"],
        "why": "Rp6,667 per KrisFlyer mile on IDR and Rp5,000 on foreign currency — with a "
               "Rp1,000,000,000 AUM requirement it is the cheapest realistic step up from "
               "Jenius if he ever parks serious money in Indonesia.",
        "catch": "Conversion capped near 25,000 miles/month, and Rp1 M AUM is a big ask. "
                 "Foreign-currency spend is where it shines — i.e. his Japan spending.",
        "source": "https://pinterpoin.com/10-kartu-kredit-terbaik-krisflyer-miles",
    },
    {
        "id": "bca_sq_kf_vi",
        "name": "BCA Singapore Airlines KrisFlyer Visa Infinite",
        "market": "Indonesia",
        "annual_fee": "premium",
        "per_mile": {"IDR": 7015},
        "reach": ["krisflyer_sq", "krisflyer_star"],
        "why": "Rp7,015/mile at Rp20jt monthly billing (Rp7,542 at Rp50jt), plus a 12,500 "
               "KrisFlyer welcome bonus and 3x miles during the twice-yearly BCA-SIA fair.",
        "catch": "Earning collapses to Rp10,800/mile below Rp20jt/month. Only worth it if "
                 "he pushes real volume through it.",
        "source": "https://pinterpoin.com/10-kartu-kredit-terbaik-krisflyer-miles",
    },
]
