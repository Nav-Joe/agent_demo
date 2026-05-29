from astral import LocationInfo

DEFAULT_CITY = "福州"

CITIES: dict[str, LocationInfo] = {
    "福州": LocationInfo("福州", "China", "Asia/Shanghai", 26.08, 119.3),
    "厦门": LocationInfo("厦门", "China", "Asia/Shanghai", 24.44, 118.08),
    "北京": LocationInfo("北京", "China", "Asia/Shanghai", 39.9, 116.4),
    "上海": LocationInfo("上海", "China", "Asia/Shanghai", 31.23, 121.47),
    "漳州": LocationInfo("漳州", "China", "Asia/Shanghai", 24.51, 117.64),
    "泉州": LocationInfo("泉州", "China", "Asia/Shanghai", 24.87, 118.68),
    "安溪": LocationInfo("安溪", "China", "Asia/Shanghai", 25.06, 118.19),
    "连江": LocationInfo("连江", "China", "Asia/Shanghai", 26.20, 119.54),
}


def extract_city(query: str) -> str:
    for city in CITIES:
        if city in query:
            return city
    return DEFAULT_CITY
