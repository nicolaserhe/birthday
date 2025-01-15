from skyfield.api import load
import numpy as np
from datetime import datetime, timedelta

# 加载天文学数据
ephemeris = load('de421.bsp')  # 使用默认的 de421 数据文件
ts = load.timescale()

# 定义地球、月球和太阳
earth = ephemeris['earth']
moon = ephemeris['moon']
sun = ephemeris['sun']


def find_new_moon(start_time, end_time, num_points=1000):
    """
    查找指定时间范围内最近的日月合朔（新月）时刻。

    参数：
    - start_time: 起始时间（Skyfield Time 对象）
    - end_time: 结束时间（Skyfield Time 对象）
    - num_points: 时间点数量（默认 1000）

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


# 定义时间范围
start_time = ts.utc(2000, 11, 20)  # 开始时间
end_time = ts.utc(2000, 11, 31)  # 结束时间

try:
    # 查找新月时刻
    new_moon_time = find_new_moon(start_time, end_time)

    # 将 UTC 时间转换为北京时间（CST，UTC+8）
    new_moon_utc = new_moon_time.utc_iso()  # 获取UTC时间
    new_moon_datetime = datetime.strptime(
            new_moon_utc, "%Y-%m-%dT%H:%M:%SZ"
            )  # 转换为datetime对象

    # 增加8小时得到北京时间
    new_moon_datetime_beijing = new_moon_datetime + timedelta(hours=8)
    # 输出北京时间
    print('下次新月的时刻（北京时间）是：', new_moon_datetime_beijing.strftime('%Y-%m-%dT%H:%M:%S'))

except Exception as e:
    print("计算新月时刻时发生错误：", e)
