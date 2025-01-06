from lunarcalendar import Lunar
from datetime import datetime, timedelta
from dataclasses import dataclass
import ephem
from skyfield.api import load
import numpy as np
import astronomical_events


# 岁名列表
TAISUI_FIRST = [
    "焉逢", "端蒙", "游兆", "强梧", "徒维", "祝犁", "商横", "昭阳", "横艾", "尚章"
]
TAISUI_LAST = [
    "困敦", "赤奋若", "摄提格", "单阏", "执徐", "大荒落", "敦牂", "协洽", "涒滩", "作噩", "淹茂", "大渊献"
]

# 天干和地支列表
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


# 生日信息
@dataclass
class BirthdayInfo:
    solar_birthday: datetime = None
    lunar_birthday: datetime = None
    taisui_name: str = None
    lunar_conjunction: datetime = None
    winter_solstice: datetime = None

    def calc_birthdayInfo(self):
        # 取得农历生日
        self.lunar_birthday = Lunar.from_date(self.solar_birthday)

        # 计算岁名
        self.taisui_name = get_suiming(self.solar_birthday)

        # 计算岁首合朔时刻
        self.lunar_conjunction = calculate_lunar_conjunction_at_new_year(self.solar_birthday)

        # 计算冬至时刻
        self.winter_solstice = calculate_winter_solstice_at_new_year(self.solar_birthday)

    # 打印生日信息的函数
    def print_birthdayInfo(self):
        print(f"岁名 {self.taisui_name}")
        # print(f"前十一月{}朔{}日冬至")
        print(f"合朔时刻: {self.lunar_conjunction}")
        print(f"冬至时刻: {self.winter_solstice}")
        # lunar_birthday = Lunar.fromSolar(solar_birthday)
        # base_date = Lunar(birthdayInfo.winter_solstice.year, 11, 1).to_date()    # 转换为公历日期
        # print(f"前十一月{}朔{}日冬至")
        return



def get_valid_date() -> datetime:
    """
    提示用户输入日期，直到输入一个有效的日期格式。
    支持格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
    返回：解析后的日期时间对象（datetime 或 date）。
    """
    while True:
        # 打印输入提示
        print("请输入一个日期（格式：YYYY-MM-DD [HH:MM:SS]，时分秒部分可以不输入）：")

        # 获取用户输入的日期字符串
        user_input = input()

        # 尝试解析输入日期字符串
        try:
            # 如果用户没有输入时分秒部分，使用下面的格式
            if len(user_input) <= 10:  # 只包含日期部分
                input_date = datetime.strptime(user_input, "%Y-%m-%d").date()
            else:  # 包含时分秒部分
                input_date = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")

            # 如果解析成功，返回有效的日期，跳出循环
            return input_date
        except ValueError:
            # 如果解析失败，提示用户重新输入
            print("输入的日期格式不正确，请按 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式输入！")


# 计算岁名函数
def get_suiming(solar_date: datetime) -> str:
    # 基准岁名：昭阳大荒落
    base_year = 2001;

    # 以子月为岁首
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        # 如果农历在11月1日之后并且阳历和农历年相等, 岁阳进入下一年
        year = solar_date.year + 1
    else:
        # 否则, 岁阳在当年
        year = solar_date.year

    # 计算日期差（年数）
    delta_years = year - base_year

    # 计算岁名索引
    taisui_first_index = (delta_years + 7) % 10 # 天干周期是10, 7是昭阳序号
    taisui_last_index = (delta_years + 5) % 12  # 地支周期是12, 5是大荒落序号

    # 获取对应的岁名
    first = TAISUI_FIRST[taisui_first_index]
    last = TAISUI_LAST[taisui_last_index]

    # 返回岁名
    return f"{first}{last}"


# 计算干支日的函数
def get_ganzhi_day(solar_date: datetime) -> str:
    # 基准日期：昭阳大荒落 子月戊子朔
    base_date = Lunar(2000, 11, 1).to_date()    # 转换为公历日期

    # 计算日期差（天数）
    delta_days = (solar_date - base_date).days

    # 计算天干和地支的索引
    heavenly_stem_index = (delta_days + 4) % 10 # 天干周期是10, 4是前大余天干序号
    earthly_branch_index = delta_days % 12      # 地支周期是12

    # 获取对应的天干和地支
    stem = HEAVENLY_STEMS[heavenly_stem_index]
    branch = EARTHLY_BRANCHES[earthly_branch_index]

    # 返回干支日
    return f"{stem}{branch}"


def calculate_lunar_conjunction_at_new_year(solar_date: datetime) -> datetime:
    # 以子月为岁首
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        # 如果农历在11月1日之后并且阳历和农历年相等, 计算当年农历十一月日月合朔时刻
        year = solar_date.year
    else:
        # 否则, 计算前一年日月合朔时刻
        year = solar_date.year - 1

    # 获取农历11月1日的日月合朔时刻
    return astronomical_events.calculate_lunar_conjunction(year, 11)


def calculate_winter_solstice_at_new_year(solar_date: datetime) -> datetime:
    # 以子月为岁首
    lunar_date = Lunar.from_date(solar_date)
    if lunar_date.month >= 11 and lunar_date.year == solar_date.year:
        # 如果农历在11月1日之后并且阳历和农历年相等, 计算当年农历十一月冬至时刻
        year = solar_date.year
    else:
        # 否则, 计算前一年冬至时刻
        year = solar_date.year - 1

    # 获取农历11月1日的冬至时刻
    return astronomical_events.calculate_winter_solstice(year)

# 主函数
def main():
    birthdayInfo = BirthdayInfo()

    # 取得阳历生日
    birthdayInfo.solar_birthday = get_valid_date()

    # 计算生日信息
    birthdayInfo.calc_birthdayInfo()

    # 打印生日信息
    birthdayInfo.print_birthdayInfo()


# 使用 __name__ == "__main__" 来判断模块是否作为主程序运行
if __name__ == "__main__":
    main()
