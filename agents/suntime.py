from datetime import datetime
import logging

import pytz
from astral.sun import sun

from agents.cities import CITIES, DEFAULT_CITY, extract_city

logger = logging.getLogger(__name__)


class SunTimeAgent:
    def __init__(self):
        self.tz = pytz.timezone("Asia/Shanghai")

    def run(self, query: str) -> str:
        city = extract_city(query)
        location = CITIES.get(city, CITIES[DEFAULT_CITY])

        today = datetime.now(self.tz).date()
        try:
            s = sun(location.observer, date=today, tzinfo=self.tz)

            sunrise = s["sunrise"].strftime("%H:%M")
            sunset = s["sunset"].strftime("%H:%M")
            dawn = s["dawn"].strftime("%H:%M")
            dusk = s["dusk"].strftime("%H:%M")
            day_length = s["sunset"] - s["sunrise"]

            return (
                f"📍 {city} 今日日出日落：\n"
                f"🌅 日出：{sunrise}\n"
                f"🌇 日落：{sunset}\n"
                f"🌄 黎明：{dawn}\n"
                f"🌆 黄昏：{dusk}\n"
                f"⏱️ 昼长：约{day_length}"
            )
        except Exception as e:
            logger.error("日出日落计算失败: %s", e)
            return f"计算日出日落时出错：{str(e)}"


if __name__ == "__main__":
    agent = SunTimeAgent()
    print(agent.run("福州今天日出几点"))
