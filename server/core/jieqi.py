import os
import math
from skyfield.api import load
from skyfield import almanac
from datetime import datetime, timedelta, timezone

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

ts  = load.timescale()
eph = load(os.path.join(_DATA_DIR, 'de440.bsp'))
earth = eph['earth']
sun   = eph['sun']


def solar_longitude(t) -> float:
    astrometric = earth.at(t).observe(sun).apparent()
    lat, lon, _ = astrometric.ecliptic_latlon(epoch=t)
    return lon.degrees % 360.0


def find_solar_lon(year: int, target: float, month_lo=4, month_hi=8) -> datetime:
    t_lo = ts.utc(year, month_lo, 1)
    t_hi = ts.utc(year, month_hi, 28)
    step_days = 0.5
    lo = hi = None
    t = t_lo
    prev = solar_longitude(t)
    while t.tt < t_hi.tt:
        t = ts.tt_jd(t.tt + step_days)
        curr = solar_longitude(t)
        d_prev = (prev - target + 180) % 360 - 180
        d_curr = (curr - target + 180) % 360 - 180
        if abs(d_prev) < 20 and d_prev * d_curr <= 0:
            lo = ts.tt_jd(t.tt - step_days)
            hi = t
            break
        prev = curr

    if lo is None:
        raise ValueError(f"未找到黄经 {target}° 在 {year}/{month_lo}~{month_hi}")

    for _ in range(80):
        mid_tt = (lo.tt + hi.tt) / 2
        mid = ts.tt_jd(mid_tt)
        d_mid = (solar_longitude(mid) - target + 180) % 360 - 180
        d_lo  = (solar_longitude(lo)  - target + 180) % 360 - 180
        if abs(d_mid) < 1e-10:
            break
        if d_lo * d_mid <= 0:
            hi = mid
        else:
            lo = mid

    return mid.utc_datetime()


JIEQI = [
    ("小寒", 285), ("大寒", 300), ("立春", 315), ("雨水", 330),
    ("惊蛰", 345), ("春分",   0), ("清明",  15), ("谷雨",  30),
    ("立夏",  45), ("小满",  60), ("芒种",  75), ("夏至",  90),
    ("小暑", 105), ("大暑", 120), ("立秋", 135), ("处暑", 150),
    ("白露", 165), ("秋分", 180), ("寒露", 195), ("霜降", 210),
    ("立冬", 225), ("小雪", 240), ("大雪", 255), ("冬至", 270),
]

JIEQI_MONTH_RANGE = {
    285:(1,1), 300:(1,2),  315:(1,3),  330:(2,3),
    345:(2,3),  0:(3,4),    15:(3,5),   30:(4,5),
    45:(4,6),   60:(5,6),   75:(5,7),   90:(6,7),
    105:(6,8),  120:(7,9),  135:(7,9),  150:(8,9),
    165:(8,10), 180:(9,10), 195:(9,11), 210:(10,11),
    225:(10,12),240:(11,12),255:(11,12),270:(12,1),
}


def main(year: int, extra_lon: float = None):
    CST = timezone(timedelta(hours=8))
    print(f"\n{'='*52}")
    print(f"  {year} 年二十四节气（北京时间）")
    print(f"{'='*52}")
    print(f"  {'节气':<6} {'黄经':>5}  {'北京时间':<22}")
    print(f"  {'-'*48}")

    for name, lon in JIEQI:
        m0, m1 = JIEQI_MONTH_RANGE[lon]
        month_end = m1 if m1 >= m0 else 12
        try:
            utc_dt = find_solar_lon(year, lon, month_lo=max(1, m0 - 1), month_hi=min(12, month_end + 1))
            cst_dt = utc_dt.astimezone(CST)
            print(f"  {name:<6} {lon:>5}°  {cst_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"  {name:<6} {lon:>5}°  ERROR: {e}")

    if extra_lon is not None:
        print(f"\n{'='*52}")
        print(f"  指定黄经 {extra_lon}° 在 {year} 年的时刻")
        print(f"{'='*52}")
        try:
            utc_dt = find_solar_lon(year, extra_lon, month_lo=1, month_hi=12)
            cst_dt = utc_dt.astimezone(CST)
            print(f"  黄经 {extra_lon}°：{cst_dt.strftime('%Y-%m-%d %H:%M:%S')} 北京时间")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == '__main__':
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else datetime.now().year
    extra = float(sys.argv[2]) if len(sys.argv) > 2 else None
    main(year, extra)
