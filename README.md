# 生辰推算

输入公历生日，推算农历、岁名、干支与天文时刻。

基于 Skyfield + NASA JPL DE421 星历的精确天文计算，支持亮色/暗色主题、桌面/移动端响应式。

## 功能

- 农历生日换算
- 岁名（太岁）
- 年月日干支
- 冬至、合朔天文时刻
- 太阳黄经
- 当年 24 节气（冬至起排）

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite |
| 后端 | FastAPI + Skyfield |
| 星历 | NASA JPL DE421 |

## 本地运行

### 后端

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
uvicorn server.main:app --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`，API 请求自动代理到后端 8000 端口。

## 项目结构

```
├── server/
│   ├── main.py                      # FastAPI 入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                  # 主页面
│   │   ├── components/
│   │   │   ├── DatePicker.vue       # 日历选择器（年月月三级跳转）
│   │   │   └── TimePicker.vue       # 圆形表盘时间选择器
│   │   ├── style.css                # 全局样式 / 主题变量
│   │   └── main.js
│   └── vite.config.js
├── astronomical_events.py           # 天文计算（冬至、合朔）
├── solar_longitude_calculator.py    # 太阳黄经 / 节气计算
├── birthdays.py                     # 生日数据模型
└── de421.bsp                        # JPL 星历文件
```
