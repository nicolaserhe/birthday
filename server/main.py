import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import server.core.birthdays as birthdays
import server.core.jieqi as jieqi_calc

CST = timezone(timedelta(hours=8))

jieqi_cache = {}
jieqi_cache_lock = asyncio.Lock()


def calc_jieqi(year: int) -> list:
    results = []
    for name, lon in jieqi_calc.JIEQI:
        m0, m1 = jieqi_calc.JIEQI_MONTH_RANGE[lon]
        month_end = m1 if m1 >= m0 else 12
        try:
            utc_dt = jieqi_calc.find_solar_lon(
                year, lon,
                month_lo=max(1, m0 - 1),
                month_hi=min(12, month_end + 1),
            )
            cst_dt = utc_dt.astimezone(CST)
            results.append({
                "name": name,
                "longitude": lon,
                "datetime": cst_dt.strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as e:
            results.append({"name": name, "longitude": lon, "error": str(e)})
    return results


async def ensure_jieqi_cached(year: int):
    if year in jieqi_cache:
        return
    async with jieqi_cache_lock:
        if year in jieqi_cache:
            return
        loop = asyncio.get_running_loop()
        jieqi_cache[year] = await loop.run_in_executor(None, calc_jieqi, year)


async def jieqi_keeper():
    while True:
        now = datetime.now(CST)
        for y in (now.year, now.year + 1):
            await ensure_jieqi_cached(y)
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    now = datetime.now(CST)
    await ensure_jieqi_cached(now.year)
    await ensure_jieqi_cached(now.year + 1)
    task = asyncio.create_task(jieqi_keeper())
    yield
    task.cancel()


app = FastAPI(title="Birthday API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthdayRequest(BaseModel):
    date: str


@app.post("/api/birthday")
def calc_birthday(req: BirthdayRequest):
    try:
        if len(req.date) <= 10:
            solar_date = datetime.strptime(req.date, "%Y-%m-%d")
        else:
            solar_date = datetime.strptime(req.date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return {"error": "日期格式不正确，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS"}

    info = birthdays.BirthdayInfo()
    info.solar_birthday = solar_date
    info.calc_birthdayInfo()

    taisui_name = info.taisui_name

    ganzhi_at_new_year = birthdays.get_ganzhi_day(info.lunar_conjunction.date())
    ganzhi_winter_solstice = birthdays.get_ganzhi_day(info.winter_solstice.date())

    ganzhi_at_month = birthdays.get_ganzhi_day(info.lunar_conjunction_birthday.date())
    ganzhi_at_birthday = birthdays.get_ganzhi_day(info.solar_birthday.date())

    month_str = (
        f"闰{birthdays.LUNAR_MONTHS[info.lunar_birthday.month - 1]}月"
        if info.lunar_birthday.isleap
        else f"{birthdays.LUNAR_MONTHS[info.lunar_birthday.month - 1]}月"
    )

    lunar_str = (
        f"闰{birthdays.LUNAR_MONTHS[info.lunar_birthday.month - 1]}月{birthdays.LUNAR_DAYS[info.lunar_birthday.day - 1]}"
        if info.lunar_birthday.isleap
        else f"{birthdays.LUNAR_MONTHS[info.lunar_birthday.month - 1]}月{birthdays.LUNAR_DAYS[info.lunar_birthday.day - 1]}"
    )

    return {
        "taisui_name": taisui_name,
        "solar_birthday": info.solar_birthday.strftime("%Y-%m-%d %H:%M:%S"),
        "lunar_birthday": lunar_str,
        "lunar_conjunction": info.lunar_conjunction.strftime("%Y-%m-%d %H:%M:%S"),
        "lunar_conjunction_birthday": info.lunar_conjunction_birthday.strftime("%Y-%m-%d %H:%M:%S"),
        "winter_solstice": info.winter_solstice.strftime("%Y-%m-%d %H:%M:%S"),
        "sun_longitude": round(info.longitude, 6),
        "ganzhi_new_year": ganzhi_at_new_year,
        "ganzhi_winter_solstice": ganzhi_winter_solstice,
        "ganzhi_month": ganzhi_at_month,
        "ganzhi_birthday": ganzhi_at_birthday,
        "month_desc": f"{month_str}{ganzhi_at_month}朔{ganzhi_at_birthday}日出生",
        "year_desc": f"前十一月{ganzhi_at_new_year}朔{ganzhi_winter_solstice}日冬至",
    }


@app.get("/api/jieqi/{year}")
async def get_jieqi(year: int):
    await ensure_jieqi_cached(year)
    return jieqi_cache[year]


@app.get("/api/health")
def health():
    return {"status": "ok"}
