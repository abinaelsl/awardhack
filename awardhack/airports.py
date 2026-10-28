"""Airport coordinates + distances for award pricing (great-circle; TPM is typically 0-5% higher)."""

from __future__ import annotations
import math

# code: (name, country, region, lat, lon)
# region keys used by the chart engine (see data/charts.json "regions")
AIRPORTS: dict[str, tuple] = {
    # --- Japan
    "FUK": ("Fukuoka", "JP", "JAPAN", 33.5859, 130.4506),
    "NRT": ("Tokyo Narita", "JP", "JAPAN", 35.7720, 140.3929),
    "HND": ("Tokyo Haneda", "JP", "JAPAN", 35.5494, 139.7798),
    "KIX": ("Osaka Kansai", "JP", "JAPAN", 34.4342, 135.2322),
    "ITM": ("Osaka Itami", "JP", "JAPAN", 34.7855, 135.4382),
    "NGO": ("Nagoya Chubu", "JP", "JAPAN", 34.8584, 136.8054),
    "CTS": ("Sapporo", "JP", "JAPAN", 42.7752, 141.6923),
    "OKA": ("Okinawa Naha", "JP", "JAPAN", 26.1958, 127.6459),
    "HIJ": ("Hiroshima", "JP", "JAPAN", 34.4361, 132.9194),
    # --- Korea / Greater China
    "ICN": ("Seoul Incheon", "KR", "N_ASIA2", 37.4602, 126.4407),
    "GMP": ("Seoul Gimpo", "KR", "N_ASIA2", 37.5583, 126.7906),
    "PUS": ("Busan", "KR", "N_ASIA2", 35.1795, 128.9382),
    "TPE": ("Taipei Taoyuan", "TW", "N_ASIA1", 25.0777, 121.2328),
    "HKG": ("Hong Kong", "HK", "N_ASIA1", 22.3080, 113.9185),
    "MFM": ("Macau", "MO", "N_ASIA1", 22.1496, 113.5915),
    "PVG": ("Shanghai Pudong", "CN", "N_ASIA1", 31.1443, 121.8083),
    "SHA": ("Shanghai Hongqiao", "CN", "N_ASIA1", 31.1979, 121.3363),
    "PEK": ("Beijing Capital", "CN", "N_ASIA1", 40.0799, 116.6031),
    "PKX": ("Beijing Daxing", "CN", "N_ASIA1", 39.5098, 116.4105),
    "CAN": ("Guangzhou", "CN", "N_ASIA1", 23.3924, 113.2988),
    "SZX": ("Shenzhen", "CN", "N_ASIA1", 22.6393, 113.8107),
    "CTU": ("Chengdu", "CN", "N_ASIA1", 30.5785, 103.9471),
    "XIY": ("Xian", "CN", "N_ASIA1", 34.4471, 108.7516),
    # --- Southeast Asia 1 (SG/MY/BN) and 2
    "SIN": ("Singapore", "SG", "SE_ASIA1", 1.3644, 103.9915),
    "KUL": ("Kuala Lumpur", "MY", "SE_ASIA1", 2.7456, 101.7099),
    "BWN": ("Brunei", "BN", "SE_ASIA1", 4.9442, 114.9283),
    "CGK": ("Jakarta", "ID", "SE_ASIA2", -6.1256, 106.6559),
    "DPS": ("Bali Denpasar", "ID", "SE_ASIA2", -8.7482, 115.1672),
    "SUB": ("Surabaya", "ID", "SE_ASIA2", -7.3798, 112.7868),
    "BKK": ("Bangkok Suvarnabhumi", "TH", "SE_ASIA2", 13.6900, 100.7501),
    "DMK": ("Bangkok Don Mueang", "TH", "SE_ASIA2", 13.9126, 100.6068),
    "HKT": ("Phuket", "TH", "SE_ASIA2", 8.1132, 98.3169),
    "CNX": ("Chiang Mai", "TH", "SE_ASIA2", 18.7669, 98.9626),
    "SGN": ("Ho Chi Minh City", "VN", "SE_ASIA2", 10.8188, 106.6520),
    "HAN": ("Hanoi", "VN", "SE_ASIA2", 21.2212, 105.8072),
    "DAD": ("Da Nang", "VN", "SE_ASIA2", 16.0439, 108.1994),
    "MNL": ("Manila", "PH", "SE_ASIA2", 14.5086, 121.0198),
    "CEB": ("Cebu", "PH", "SE_ASIA2", 10.3075, 123.9794),
    "PNH": ("Phnom Penh", "KH", "SE_ASIA2", 11.5466, 104.8441),
    "RGN": ("Yangon", "MM", "SE_ASIA2", 16.9073, 96.1332),
    "VTE": ("Vientiane", "LA", "SE_ASIA2", 17.9883, 102.5633),
    # --- South Asia
    "DEL": ("Delhi", "IN", "S_ASIA", 28.5562, 77.1000),
    "BOM": ("Mumbai", "IN", "S_ASIA", 19.0896, 72.8656),
    "BLR": ("Bengaluru", "IN", "S_ASIA", 13.1986, 77.7066),
    "MAA": ("Chennai", "IN", "S_ASIA", 12.9941, 80.1709),
    "CMB": ("Colombo", "LK", "S_ASIA", 7.1808, 79.8841),
    "MLE": ("Male", "MV", "S_ASIA", 4.1918, 73.5291),
    "KTM": ("Kathmandu", "NP", "S_ASIA", 27.6966, 85.3591),
    "DAC": ("Dhaka", "BD", "S_ASIA", 23.8433, 90.3978),
    # --- Middle East / Africa
    "DOH": ("Doha", "QA", "MIDDLE_EAST", 25.2731, 51.6081),
    "DXB": ("Dubai", "AE", "MIDDLE_EAST", 25.2532, 55.3657),
    "AUH": ("Abu Dhabi", "AE", "MIDDLE_EAST", 24.4330, 54.6511),
    "IST": ("Istanbul", "TR", "EUROPE", 41.2753, 28.7519),
    "CAI": ("Cairo", "EG", "AFRICA", 30.1219, 31.4056),
    "JNB": ("Johannesburg", "ZA", "AFRICA", -26.1367, 28.2411),
    # --- Oceania
    "SYD": ("Sydney", "AU", "SW_PACIFIC", -33.9399, 151.1753),
    "MEL": ("Melbourne", "AU", "SW_PACIFIC", -37.6690, 144.8410),
    "PER": ("Perth", "AU", "SW_PACIFIC", -31.9385, 115.9672),
    "BNE": ("Brisbane", "AU", "SW_PACIFIC", -27.3842, 153.1175),
    "AKL": ("Auckland", "NZ", "SW_PACIFIC", -37.0082, 174.7850),
    "GUM": ("Guam", "GU", "GUAM", 13.4834, 144.7960),
    # --- Europe
    "LHR": ("London Heathrow", "GB", "EUROPE", 51.4700, -0.4543),
    "CDG": ("Paris CDG", "FR", "EUROPE", 49.0097, 2.5479),
    "FRA": ("Frankfurt", "DE", "EUROPE", 50.0379, 8.5622),
    "MUC": ("Munich", "DE", "EUROPE", 48.3538, 11.7861),
    "AMS": ("Amsterdam", "NL", "EUROPE", 52.3105, 4.7683),
    "HEL": ("Helsinki", "FI", "EUROPE", 60.3172, 24.9633),
    "ZRH": ("Zurich", "CH", "EUROPE", 47.4647, 8.5492),
    "FCO": ("Rome Fiumicino", "IT", "EUROPE", 41.8003, 12.2389),
    # --- North America
    "JFK": ("New York JFK", "US", "N_AMERICA", 40.6413, -73.7781),
    "EWR": ("Newark", "US", "N_AMERICA", 40.6895, -74.1745),
    "LAX": ("Los Angeles", "US", "N_AMERICA", 33.9416, -118.4085),
    "SFO": ("San Francisco", "US", "N_AMERICA", 37.6213, -122.3790),
    "SEA": ("Seattle", "US", "N_AMERICA", 47.4502, -122.3088),
    "ORD": ("Chicago O'Hare", "US", "N_AMERICA", 41.9742, -87.9073),
    "DFW": ("Dallas", "US", "N_AMERICA", 32.8998, -97.0403),
    "YVR": ("Vancouver", "CA", "N_AMERICA", 49.1967, -123.1815),
    "HNL": ("Honolulu", "US", "HAWAII", 21.3187, -157.9224),
}

R = 6371.0088  # km


def coords(code: str) -> tuple[float, float]:
    return AIRPORTS[code.upper()][3], AIRPORTS[code.upper()][4]


def distance_km(a: str, b: str) -> float:
    lat1, lon1 = map(math.radians, coords(a))
    lat2, lon2 = map(math.radians, coords(b))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def distance_mi(a: str, b: str) -> float:
    return distance_km(a, b) / 1.609344


def region(code: str) -> str:
    return AIRPORTS[code.upper()][2]


def name(code: str) -> str:
    return AIRPORTS[code.upper()][0]


def lookup(query: str) -> list[str]:
    """Fuzzy lookup: exact code, prefix of name/city."""
    q = query.strip().upper()
    if q in AIRPORTS:
        return [q]
    hits = [c for c, v in AIRPORTS.items() if q and (q in c or q in v[0].upper())]
    return hits
