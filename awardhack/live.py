"""Live award-price check against AwardTool's public route pages (no login, no API key).

AwardTool publishes, per route, the lowest award it actually OBSERVED in the last 30 days,
broken down by program. That is the only public, program-agnostic cross-check we can get for
free, so it is used as a sanity layer on top of the static charts.

If the network is unavailable the CLI simply skips this layer.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
BASE = "https://www.awardtool.com/award-flights/"
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "awardhack")
CACHE_TTL_H = 12

# AwardTool slugs use a city name, not the airport's full name.
CITY = {
    "FUK": "fukuoka", "NRT": "tokyo", "HND": "tokyo", "KIX": "osaka", "ITM": "osaka",
    "NGO": "nagoya", "CTS": "sapporo", "OKA": "okinawa", "HIJ": "hiroshima",
    "ICN": "seoul", "GMP": "seoul", "PUS": "busan", "TPE": "taipei", "HKG": "hong-kong",
    "MFM": "macau", "PVG": "shanghai", "SHA": "shanghai", "PEK": "beijing", "PKX": "beijing",
    "CAN": "guangzhou", "SZX": "shenzhen", "CTU": "chengdu", "XIY": "xian",
    "SIN": "singapore", "KUL": "kuala-lumpur", "BWN": "brunei", "CGK": "jakarta",
    "DPS": "bali", "SUB": "surabaya", "BKK": "bangkok", "DMK": "bangkok", "HKT": "phuket",
    "CNX": "chiang-mai", "SGN": "ho-chi-minh-city", "HAN": "hanoi", "DAD": "da-nang",
    "MNL": "manila", "CEB": "cebu", "PNH": "phnom-penh", "RGN": "yangon", "VTE": "vientiane",
    "DEL": "delhi", "BOM": "mumbai", "BLR": "bengaluru", "MAA": "chennai", "CMB": "colombo",
    "MLE": "male", "KTM": "kathmandu", "DAC": "dhaka",
    "DOH": "doha", "DXB": "dubai", "AUH": "abu-dhabi", "IST": "istanbul", "CAI": "cairo",
    "JNB": "johannesburg", "SYD": "sydney", "MEL": "melbourne", "PER": "perth",
    "BNE": "brisbane", "AKL": "auckland", "GUM": "guam",
    "LHR": "london", "CDG": "paris", "FRA": "frankfurt", "MUC": "munich", "AMS": "amsterdam",
    "HEL": "helsinki", "ZRH": "zurich", "FCO": "rome",
    "JFK": "new-york", "EWR": "newark", "LAX": "los-angeles", "SFO": "san-francisco",
    "SEA": "seattle", "ORD": "chicago", "DFW": "dallas", "YVR": "vancouver", "HNL": "honolulu",
}


def _slug(code: str) -> str:
    return f"{CITY.get(code.upper(), code.lower())}-{code.lower()}"


def _cache_path(from_c: str, to_c: str) -> str:
    os.makedirs(CACHE, exist_ok=True)
    return os.path.join(CACHE, f"{from_c}-{to_c}.json")


def _fetch(url: str, timeout: int = 25) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return None
            return r.read().decode("utf-8", "ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


_LOWEST = re.compile(
    r"Lowest\s+(economy|premium economy|business class|business|first class)\s*:?\s*"
    r"\**\s*([\d,]+)\s*(?:miles|points|pts|Avios)\s*\+\s*\$([\d,.]+)\s*\(([^)]+)\)",
    re.I)
_ROW = re.compile(r"\[([^\]]{3,60})\]\(https://www\.awardtool\.com/award-flights/[^)]+\)"
                  r"\s*\|\s*([\d,]+)\s*(?:pts|miles|points|Avios)[^|]*\|\s*"
                  r"(?:([\d,]+)\s*(?:pts|miles|points|Avios)[^|]*)?\|", re.I)


def fetch_route(origin: str, destination: str, ignore_cache: bool = False) -> dict:
    """Return {'ok':bool,'observed':{cabin:[(program,miles,taxes_usd)]},'as_of':ts,...}"""
    o, d = origin.upper(), destination.upper()
    cp = _cache_path(o, d)
    if not ignore_cache and os.path.exists(cp):
        try:
            blob = json.load(open(cp, encoding="utf-8"))
            age_h = (datetime.now(timezone.utc).timestamp() - blob["fetched_ts"]) / 3600
            if age_h < CACHE_TTL_H:
                blob["cached"] = True
                return blob
        except Exception:
            pass

    url = f"{BASE}{_slug(o)}-to-{_slug(d)}"
    html = _fetch(url)
    if html is None:
        return {"ok": False, "error": f"could not fetch {url}", "url": url}

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    observed: dict[str, list] = {}
    for m in _LOWEST.finditer(text):
        cabin_raw = m.group(1).lower()
        cabin = {"economy": "Y", "premium economy": "W", "business class": "J",
                 "business": "J", "first class": "F"}[cabin_raw]
        miles = int(m.group(2).replace(",", ""))
        taxes = float(m.group(3).replace(",", ""))
        observed.setdefault(cabin, []).append((m.group(4).strip(), miles, taxes))

    programs = re.findall(r"Programs with award space seen\s+(\d+) of (\d+)", text)
    stale = "data snapshot" in text
    return {
        "ok": bool(observed),
        "url": url,
        "observed": observed,
        "coverage": programs[0] if programs else None,
        "fetched_ts": datetime.now(timezone.utc).timestamp(),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "snapshot": stale,
    }


def fx_rate(base: str, quote: str = "JPY", default: float = 150.0) -> float:
    """Daily cached FX rate via frankfurter.app; falls back to `default`."""
    base, quote = base.upper(), quote.upper()
    if base == quote:
        return 1.0
    cp = os.path.join(CACHE, f"{base}{quote}.json")
    if os.path.exists(cp):
        try:
            blob = json.load(open(cp, encoding="utf-8"))
            if (datetime.now(timezone.utc).timestamp() - blob["ts"]) < 86400:
                return blob["rate"]
        except Exception:
            pass
    payload = _fetch(f"https://api.frankfurter.app/latest?from={base}&to={quote}", timeout=15)
    if payload:
        try:
            rate = float(json.loads(payload)["rates"][quote])
            os.makedirs(CACHE, exist_ok=True)
            json.dump({"rate": rate, "ts": datetime.now(timezone.utc).timestamp()},
                      open(cp, "w", encoding="utf-8"))
            return rate
        except Exception:
            pass
    return default


def fx_usdjpy(default: float = 150.0) -> float:
    return fx_rate("USD", "JPY", default)
