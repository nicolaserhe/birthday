import os
from skyfield.api import load
from skyfield import almanac
from datetime import datetime, timedelta, timezone
from lunarcalendar import Lunar
import pytz

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

ephemeris = load(os.path.join(_DATA_DIR, 'de421.bsp'))
ts = load.timescale()

earth = ephemeris['earth']
moon = ephemeris['moon']
sun = ephemeris['sun']

CST = timezone(timedelta(hours=8))


def calculate_winter_solstice(year: int) -> datetime:
    """使用 skyfield almanac 计算冬至时刻（高效）"""
    t0 = ts.utc(year, 12, 15)
    t1 = ts.utc(year, 12, 31)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(ephemeris))
    for t, ev in zip(times, events):
        if ev == 3:  # 3 = 冬至 (December solstice)
            return t.utc_datetime().replace(tzinfo=timezone.utc).astimezone(CST).replace(tzinfo=None)
    # fallback: 跨年搜索
    t0 = ts.utc(year + 1, 1, 1)
    t1 = ts.utc(year + 1, 1, 10)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(ephemeris))
    for t, ev in zip(times, events):
        if ev == 2:
            return t.utc_datetime().replace(tzinfo=timezone.utc).astimezone(CST).replace(tzinfo=None)
    raise ValueError(f"未找到 {year} 年冬至")


def calculate_lunar_conjunction(lunar_date: Lunar) -> datetime:
    """使用 skyfield almanac 计算合朔时刻（高效）"""
    solar_date = lunar_date.to_date()
    t0 = ts.utc(solar_date.year, solar_date.month, max(1, solar_date.day - 3))
    t1_day = solar_date.day + 3
    if t1_day <= 28:
        t1 = ts.utc(solar_date.year, solar_date.month, t1_day)
    elif solar_date.month < 12:
        t1 = ts.utc(solar_date.year, solar_date.month + 1, 1)
    else:
        t1 = ts.utc(solar_date.year + 1, 1, 1)

    moon_phase_fn = almanac.moon_phases(ephemeris)
    times, phases = almanac.find_discrete(t0, t1, moon_phase_fn)

    target_date = ts.utc(solar_date.year, solar_date.month, solar_date.day)
    best = None
    best_diff = float('inf')
    for t, p in zip(times, phases):
        if p == 0:  # 0 = 新月（合朔）
            diff = abs(t.tt - target_date.tt)
            if diff < best_diff:
                best_diff = diff
                best = t

    if best is None:
        raise ValueError(f"未找到 {solar_date} 附近的合朔")

    return best.utc_datetime().replace(tzinfo=timezone.utc).astimezone(CST).replace(tzinfo=None)


def calculate_sun_longitude(solar_date: datetime) -> float:
    """使用 skyfield 计算太阳视黄经（不含 astropy 依赖）"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    date_beijing = beijing_tz.localize(solar_date)
    date_utc = date_beijing.astimezone(pytz.utc)
    t = ts.utc(date_utc)
    astrometric = earth.at(t).observe(sun).apparent()
    _, lon, _ = astrometric.ecliptic_latlon(epoch=t)
    return lon.degrees % 360
