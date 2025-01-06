# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 后端
.venv/bin/uvicorn server.main:app --port 8000          # 从项目根目录启动

# 前端
cd frontend && npm run dev                              # 开发服务器 (默认 5173, 代理 /api → :8000)
cd frontend && npm run build                            # 生产构建
```

后端依赖: `pip install -r server/requirements.txt`
前端依赖: `cd frontend && npm install`

## 架构

```
用户输入公历生日 → FastAPI → BirthdayInfo.calc_birthdayInfo()
  ├─ calculate_sun_longitude()     # 黄经 (skyfield 直接计算)
  ├─ Lunar.from_date()             # 农历换算 (lunarcalendar)
  ├─ get_suiming()                 # 岁名 (干支推算)
  ├─ calculate_lunar_conjunction() # 合朔 (skyfield almanac moon_phases)
  └─ calculate_winter_solstice()   # 冬至 (skyfield almanac seasons)
```

**项目结构**: `server/core/` 下按功能拆分：
- `birthdays.py` — 核心生日计算（岁名、干支、合朔、冬至）
- `astronomical_events.py` — 天文计算（黄经、合朔、冬至），使用 DE421 星历
- `jieqi.py` — 二十四节气计算，使用 DE440 星历

**星历**: `de421.bsp` 和 `de440.bsp` 放在 `server/data/`，模块通过 `__file__` 定位，不依赖 CWD。

**岁首规则**: 以农历十一月（子月）为岁首。如果公历生日对应的农历在十一月之后、阳历仍在同年，则岁阳进入下一年。

**节气缓存**: 后端启动时预计算今年+明年节气，每小时检查跨年。`/api/jieqi/{year}` 命中缓存直接返回，未命中现场计算并缓存。

**前端架构**: 纯 Vue 3 SFC，无路由/状态管理库。DatePicker 支持日历/月份/年份三级视图切换，TimePicker 为圆形表盘+确认/取消草稿模式。

## 主题

CSS 变量定义在 `frontend/src/style.css`，`[data-theme="dark"]` 和 `[data-theme="light"]` 两套。`document.documentElement.setAttribute('data-theme', ...)` 切换，localStorage 持久化。
