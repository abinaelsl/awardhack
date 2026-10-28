"""Transfer map: which card currency can reach which airline program.

Japanese-market focus (the user lives in Fukuoka) plus the Indonesian bank-card reality,
which is usually "KrisFlyer or nothing".
"""

from __future__ import annotations

TRANSFERS = {
    "amex_mr_jp": {
        "name": "Amex Membership Rewards (Japan)",
        "verified": "amex.co.jp — 13 airline partners, 1,000 points = 1,000 miles",
        "source": "https://www.americanexpress.com/ja-jp/point/mile-point/airline",
        "as_of": "2026-10-28",
        "ratio": "1,000 : 1,000",
        "reaches": ["ana_partner", "jal_own", "jal_oneworld", "krisflyer_sq", "krisflyer_star",
                    "avios", "asiamiles"],
        "confirmed_partners": ["ANA Mileage Club", "JAL Mileage Bank", "Air France/KLM Flying Blue",
                               "Delta SkyMiles"],
        "notes": "ANA transfers carry an annual fee (¥5,500 incl. tax, free on Platinum); "
                 "transfers are not instant — days, not minutes, so never transfer before you "
                 "have a confirmed seat. Full 13-airline list is behind the site's tab UI: "
                 "verify on amex.co.jp before moving points.",
    },
    "marriott_bonvoy": {
        "name": "Marriott Bonvoy",
        "verified": "3:1 with a 5,000-mile bonus per 60,000 points (i.e. 60k → 25k miles)",
        "source": "https://www.marriott.com/loyalty/redeem/travel/points-to-miles.mi",
        "as_of": "2026-10-28",
        "ratio": "3 : 1 (+5,000 per 60,000)",
        "reaches": ["ana_partner", "jal_own", "krisflyer_sq", "krisflyer_star", "avios",
                    "asiamiles", "turkish"],
        "notes": "The only realistic way to reach Turkish, Alaska, Avianca etc. from a "
                 "Japan-based wallet. Slow transfers (days).",
    },
    "dbs_id": {
        "name": "DBS Indonesia (digibank) reward points",
        "verified": "user-confirmed in-app path: DBS ID points -> KrisFlyer miles",
        "source": "https://www.dbs.id/digibank/id/en/kartu/kartu-digibank/digibank-mc-black",
        "as_of": "2026-10-28",
        "ratio": "varies by card tier — read the in-app conversion screen before transferring",
        "reaches": ["krisflyer_sq", "krisflyer_star"],
        "notes": "KrisFlyer-only. No ANA/JAL/Avios/Asia Miles/LifeMiles path from here, so every "
                 "DBS point lands in the one program that prices Japan-Indonesia highest.",
    },
    "jenius": {
        "name": "Jenius Credit Card (Bank BTPN) — Yay Points",
        "verified": "jenius.com/pages/yaypoints: 40,000 Yay = 30,000 KrisFlyer (Club Grow/Nurture/Bloom); "
                    "50,000 Yay = 30,000 KrisFlyer (Club Seed/Plant); 25,000 Yay = 20,000 GarudaMiles; "
                    "one conversion per airline per month, effective 1 Aug 2026",
        "source": "https://www.jenius.com/pages/yaypoints",
        "as_of": "2026-08-01",
        "ratio": "40,000 Yay : 30,000 KF (0.75/mile) | 25,000 Yay : 20,000 GarudaMiles (0.80/mile)",
        "reaches": ["krisflyer_sq", "krisflyer_star", "garudamiles_ga"],
        "notes": "The only one of his currencies with a SECOND airline partner: GarudaMiles redeems "
                 "at a slightly better Yay ratio than KrisFlyer and can be spent on Garuda's "
                 "nonstop HND/NRT-Jakarta flights. Earn is 1 Yay per Rp10,000 domestic (Club Grow+), "
                 "i.e. ~1 mile per Rp13,300 of spend.",
    },
    "id_bank_krisflyer": {
        "name": "Indonesian bank cards (Mandiri / BCA / BNI / CIMB / UOB / Danamon / HSBC ID)",
        "verified": "issuer pages — nearly all route points to KrisFlyer (some to GarudaMiles)",
        "source": "https://www.singaporeair.com/en_UK/id/ppsclub-krisflyer/earn-miles/credit-cards/",
        "as_of": "2026-10-28",
        "ratio": "varies by issuer",
        "reaches": ["krisflyer_sq", "krisflyer_star"],
        "notes": "This is the wall most people hit: Indonesian cards generally CANNOT reach "
                 "ANA, JAL, Avios, Asia Miles or LifeMiles. So if KrisFlyer is your only "
                 "currency, your leverage is (a) the SQ Saver chart, (b) the Star partner "
                 "chart, and (c) topping up with a transferable currency.",
    },
    "us_currencies": {
        "name": "US/global transferable currencies (if you hold them)",
        "verified": "AwardTool program table: Amex MR, Bilt, Capital One, Chase, Citi, Wells Fargo",
        "source": "https://www.awardtool.com/programs",
        "as_of": "2026-10-28",
        "ratio": "varies",
        "reaches": ["krisflyer_sq", "krisflyer_star", "ana_partner", "jal_oneworld", "avios",
                    "asiamiles", "turkish"],
        "notes": "Capital One / Citi reach Avianca LifeMiles and Turkish, which is where the "
                 "genuinely cheap intra-Asia business redemptions live.",
    },
    "cash_buy_miles": {
        "name": "Buying miles outright",
        "verified": "n/a — depends on the running promotion",
        "source": "https://www.lifemiles.com/",
        "ratio": "often 100–150% bonus on LifeMiles / Turkish buys",
        "reaches": ["krisflyer_sq", "ana_partner", "turkish", "avios"],
        "notes": "Buying during a 100%+ bonus can beat a cash fare on a short-notice business "
                 "ticket, but it is a cash purchase, not a points optimisation. Only do it when "
                 "the seat is confirmed available first.",
    },
}


# What he actually holds (updated 2026-10-28): Indonesian bank cards only — DBS Indonesia
# digibank and a Jenius (BTPN) card. No ANA account, JAL account lost. So the funded set is
# deliberately small.
MY_CURRENCIES = ["dbs_id", "jenius"]


def reachable(program_key: str) -> list[str]:
    return [k for k, v in TRANSFERS.items() if program_key in v["reaches"]]


def mine(program_key: str) -> list[str]:
    """Currencies he can actually move points from today (not 'could, if he opened an account')."""
    return [k for k in MY_CURRENCIES if program_key in TRANSFERS[k]["reaches"]]
