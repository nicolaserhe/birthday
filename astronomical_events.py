from skyfield.api import load
from astropy.time import Time
from astropy.coordinates import get_sun, GeocentricTrueEcliptic
from datetime import datetime, timedelta
from astropy import units as u
import numpy as np
from lunarcalendar import Lunar


# 加载天文学数据
ephemeris = load('de421.bsp')  # 使用默认的 de421 数据文件
ts = load.timescale()

# 定义地球、月球和太阳
earth = ephemeris['earth']
moon = ephemeris['moon']
sun = ephemeris['sun']


# 计算冬至时刻的函数
def calculate_winter_solstice(year: int) -> datetime:
    # 设置起始日期范围
    start_time = Time(f'{year}-12-20')
    end_time = Time(f'{year}-12-24')

    # 通过获取太阳位置找到冬至时刻
    times = np.linspace(start_time.jd, end_time.jd, 10000)  # 创建时间点
    times = Time(times, format='jd')

    # 获取每个时间点太阳的黄道坐标（转换为黄道坐标系）
    sun_coords = get_sun(times)

    # 将太阳坐标转换为黄道坐标系
    sun_coords_ecliptic = sun_coords.transform_to(GeocentricTrueEcliptic())

    # 获取太阳的黄道经度
    sun_lon = sun_coords_ecliptic.lon  # 获取太阳的黄道经度

    # 查找太阳黄道经度最接近 270 度（即冬至的经度）
    winter_solstice_time = times[np.abs(sun_lon - 270 * u.deg).argmin()]

    # 将冬至时刻转换为北京时间（加8小时）
    winter_solstice_time_utc = winter_solstice_time.datetime  # 获取 UTC 时间
    winter_solstice_time_bj = winter_solstice_time_utc + timedelta(hours=8)

    # 返回北京时间
    return winter_solstice_time_bj


def calculate_lunar_conjunction(lunar_date: Lunar) -> datetime:
    """
    计算指定年月的最近新月（合朔）时刻，并返回北京时间。

    参数:
    - year: 年份
    - month: 月份

    返回:
    - 新月时刻（北京时间）
    """
    # 将农历日期转换为阳历日期
    solar_date = lunar_date.to_date()

    # 使用 Skyfield 加载阳历日期
    start_time = ts.utc(solar_date.year, solar_date.month, solar_date.day - 1)

    # 设置一个合理的结束时间范围
    end_time = ts.utc(solar_date.year, solar_date.month, solar_date.day + 1)

    # 查找指定时间范围内最近的新月时刻
    closest_new_moon_time = find_new_moon(start_time, end_time)

    # 获取新月时刻的 UTC 时间
    new_moon_utc = closest_new_moon_time.utc_iso()

    # 将UTC时间转换为 datetime 对象
    new_moon_utc_time = datetime.fromisoformat(new_moon_utc)

    # 将UTC时间转换为北京时间（加8小时）
    new_moon_bj_time = new_moon_utc_time + timedelta(hours=8)

    # 返回北京时间
    return new_moon_bj_time


def find_new_moon(start_time, end_time, num_points=10000):
    """
    查找指定时间范围内最近的新月（合朔）时刻。

    参数：
    - start_time: 起始时间（Skyfield Time 对象）
    - end_time: 结束时间（Skyfield Time 对象）
    - num_points: 时间点数量（默认为 10000）

    返回：
    - Skyfield Time 对象，表示新月的时刻
    """
    # 逐步增加时间点
    time_step = (end_time.tt - start_time.tt) / num_points
    times = [start_time + i * time_step for i in range(num_points)]

    # 计算从地球观察到的月亮和太阳的相位角
    moon_phase_angles = []
    for time in times:
        # 使用地球作为观察者
        e = earth.at(time)  # 每次传递一个时间点
        moon_position = e.observe(moon).apparent()
        sun_position = e.observe(sun).apparent()

        # 计算月亮和太阳的视离角
        phase_angle = moon_position.separation_from(sun_position)

        # 保存相位角值
        moon_phase_angles.append(phase_angle.radians)

    # 找到相位角最小的时间点，即合朔
    min_index = np.argmin(moon_phase_angles)
    return times[min_index]
