from lunarcalendar import Lunar
from datetime import date, datetime, timedelta
from dataclasses import dataclass

from . import astronomical_events


TAISUI_FIRST = [
    "焉逢", "端蒙", "游兆", "强梧", "徒维", "祝犁", "商横", "昭阳", "横艾", "尚章"
]
TAISUI_LAST = [
    "困敦", "赤奋若", "摄提格", "单阏", "执徐", "大荒落", "敦牂", "协洽", "涒滩", "作噩", "淹茂", "大渊献"
]

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

LUNAR_MONTHS = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
LUNAR_DAYS = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
]


@dataclass
class BirthdayInfo:
    solar_birthday: datetime = None
    lunar_birthday: datetime = None
    taisui_name: str = None
    lunar_conjunction: datetime = None
    winter_solstice: datetime = None
    longitude: float = None
    lunar_conjunction_birthday: datetime = None

    def calc_birthdayInfo(self):
        self.longitude = astronomical_events.calculate_sun_longitude(self.solar_birthday)
        self.lunar_birthday = Lunar.from_date(self.solar_birthday)
        self.taisui_name = get_suiming(self.solar_birthday)
        self.lunar_conjunction = calculate_lunar_conjunction_at_new_year(self.solar_birthday)
        self.winter_solstice = calculate_winter_solstice_at_new_year(self.solar_birthday)
        self.lunar_conjunction_birthday = calculate_lunar_conjunction_at_birthday(self.solar_birthday)

    def print_birthdayInfo(self):
        print(f"岁名 {self.taisui_name}")

        ganzhi_at_new_year = get_ganzhi_day(self.lunar_conjunction.date())
        ganzhi_winter_solstice = get_ganzhi_day(self.winter_solstice.date())
        print(f"前十一月{ganzhi_at_new_year}朔{ganzhi_winter_solstice}日冬至")
        formatted_bj_time = self.lunar_conjunction.strftime('%Y-%m-%d %H:%M:%S')
        print(f"合朔时刻: {formatted_bj_time}")
        formatted_bj_time = self.winter_solstice.strftime('%Y-%m-%d %H:%M:%S')
        print(f"冬至时刻: {formatted_bj_time}")

        ganzhi_at_month = get_ganzhi_day(self.lunar_conjunction_birthday.date())
        ganzhi_at_birthday = get_ganzhi_day(self.solar_birthday.date())
        if self.lunar_birthday.isleap:
            print(f"闰{LUNAR_MONTHS[self.lunar_birthday.month - 1]}月{ganzhi_at_month}朔{ganzhi_at_birthday}日出生")
        else:
            print(f"{LUNAR_MONTHS[self.lunar_birthday.month - 1]}月{ganzhi_at_month}朔{ganzhi_at_birthday}日出生")
        formatted_bj_time = self.lunar_conjunction_birthday.strftime('%Y-%m-%d %H:%M:%S')
        print(f"合朔时刻: {formatted_bj_time}")
        formatted_bj_time = self.solar_birthday.strftime('%Y-%m-%d %H:%M:%S')
        print(f"出生时刻: {formatted_bj_time}")

        if self.lunar_birthday.isleap:
            print(f"农历生日: 闰{LUNAR_MONTHS[self.lunar_birthday.month - 1]}月{LUNAR_DAYS[self.lunar_birthday.day - 1]}")
        else:
            print(f"农历生日: {LUNAR_MONTHS[self.lunar_birthday.month - 1]}月{LUNAR_DAYS[self.lunar_birthday.day - 1]}")

        print(f"出生时刻太阳的黄经: {self.longitude}°")


def get_valid_date() -> datetime:
    while True:
        print("请输入一个日期（格式：YYYY-MM-DD [HH:MM:SS]，时分秒部分可以不输入）：")
        user_input = input()
        try:
            if len(user_input) <= 10:
                input_date = datetime.strptime(user_input, "%Y-%m-%d").date()
            else:
                input_date = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
            return input_date
        except ValueError:
            print("输入的日期格式不正确，请按 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式输入！")


def get_suiming(solar_date: date) -> str:
    base_year = 2001
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        year = solar_date.year + 1
    else:
        year = solar_date.year
    delta_years = year - base_year
    taisui_first_index = (delta_years + 7) % 10
    taisui_last_index = (delta_years + 5) % 12
    return f"{TAISUI_FIRST[taisui_first_index]}{TAISUI_LAST[taisui_last_index]}"


def get_ganzhi_day(solar_date: date) -> str:
    base_date = Lunar(2000, 11, 1).to_date()
    delta_days = (solar_date - base_date).days
    heavenly_stem_index = (delta_days + 4) % 10
    earthly_branch_index = delta_days % 12
    return f"{HEAVENLY_STEMS[heavenly_stem_index]}{EARTHLY_BRANCHES[earthly_branch_index]}"


def calculate_lunar_conjunction_at_new_year(solar_date: datetime) -> datetime:
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        lunar_date.year = solar_date.year
    else:
        lunar_date.year = solar_date.year - 1
    lunar_date.month = 11
    lunar_date.isleap = False
    lunar_date.day = 1
    return astronomical_events.calculate_lunar_conjunction(lunar_date)


def calculate_lunar_conjunction_at_birthday(solar_date: datetime) -> datetime:
    lunar_date = Lunar.from_date(solar_date)
    lunar_date.day = 1
    return astronomical_events.calculate_lunar_conjunction(lunar_date)


def calculate_winter_solstice_at_new_year(solar_date: datetime) -> datetime:
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        year = solar_date.year
    else:
        year = solar_date.year - 1
    return astronomical_events.calculate_winter_solstice(year)


def main():
    birthdayInfo = BirthdayInfo()
    birthdayInfo.solar_birthday = get_valid_date()
    birthdayInfo.calc_birthdayInfo()
    birthdayInfo.print_birthdayInfo()


if __name__ == "__main__":
    main()
