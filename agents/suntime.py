from astral import LocationInfo
from astral.sun import sun
from datetime import datetime
import pytz

class SunTimeAgent:
    def __init__(self):
        self.cities = {
            "福州": LocationInfo("福州", "China", "Asia/Shanghai", 26.08, 119.3),
            "厦门": LocationInfo("厦门", "China", "Asia/Shanghai", 24.44, 118.08),
            "北京": LocationInfo("北京", "China", "Asia/Shanghai", 39.9, 116.4),
            "上海": LocationInfo("上海", "China", "Asia/Shanghai", 31.23, 121.47),
            "漳州": LocationInfo("漳州", "China", "Asia/Shanghai", 24.51, 117.64),
            "泉州": LocationInfo("泉州", "China", "Asia/Shanghai", 24.87, 118.68),
        }
        self.tz = pytz.timezone("Asia/Shanghai")
    
    def run(self, query: str) -> str:
        city = self._extract_city(query)
        location = self.cities.get(city, self.cities["福州"])
        
        today = datetime.now(self.tz).date()
        try:
            s = sun(location.observer, date=today, tzinfo=self.tz)
            
            sunrise = s['sunrise'].strftime('%H:%M')
            sunset = s['sunset'].strftime('%H:%M')
            dawn = s['dawn'].strftime('%H:%M')
            dusk = s['dusk'].strftime('%H:%M')
            day_length = s['sunset'] - s['sunrise']
            
            return (f"📍 {city} 今日日出日落：\n"
                    f"🌅 日出：{sunrise}\n"
                    f"🌇 日落：{sunset}\n"
                    f"🌄 黎明：{dawn}\n"
                    f"🌆 黄昏：{dusk}\n"
                    f"⏱️ 昼长：约{day_length}")
        except Exception as e:
            return f"计算日出日落时出错：{str(e)}"
    
    def _extract_city(self, query: str) -> str:
        for city in self.cities:
            if city in query:
                return city
        return "福州"
#test
if __name__ == "__main__":
    agent = SunTimeAgent()
    print(agent.run("福州今天日出几点"))
