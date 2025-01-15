from skyfield.api import load
from datetime import timedelta

def find_precise_solar_longitude_bj(year, target_longitude):
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']

    # 设置时间范围
    start_time = ts.utc(year, 6, 3)
    end_time = ts.utc(year, 6, 8)

    # 计算太阳黄经
    def solar_longitude_at(t):
        astrometric = earth.at(t).observe(eph['sun'])
        longitude = astrometric.apparent().ecliptic_latlon()[1].degrees
        return longitude

    # 搜索目标黄经
    step_days = 0.001  # 更小步长以提高精度
    t = start_time
    closest_date = None
    min_difference = float('inf')

    while t < end_time:
        longitude = solar_longitude_at(t)
        difference = abs(longitude - target_longitude)

        if difference < min_difference:
            min_difference = difference
            closest_date = t

        if difference < 0.0001:  # 足够接近目标黄经
            bj_time = t.utc_datetime() + timedelta(hours=8)
            return bj_time

        t = ts.tt_jd(t.tt + step_days)

    if closest_date is not None:
        bj_time = closest_date.utc_datetime() + timedelta(hours=8)
        return f"最接近目标黄经的北京时间: {bj_time}，黄经误差: {min_difference:.6f} 度"

    return "未找到目标黄经的日期"

# 示例：查找 2025 年太阳黄经为 75.36306992446926 度的北京时间
year = 2025
target_longitude = 75.36306992446926
bj_date = find_precise_solar_longitude_bj(year, target_longitude)

print(bj_date)

