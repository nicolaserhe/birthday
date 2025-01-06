<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import DatePicker from './components/DatePicker.vue'
import TimePicker from './components/TimePicker.vue'

const now = new Date()
const dateVal = ref(now.toISOString().slice(0, 10))
const hours = String(now.getHours()).padStart(2, '0')
const mins = String(now.getMinutes()).padStart(2, '0')
const timeVal = ref(`${hours}:${mins}`)

const loading = ref(false)
const result = ref(null)
const error = ref('')
const jieqi = ref(null)
const jieqiLoading = ref(false)
const jieqiCache = {}

const hasResult = computed(() => result.value !== null)
const birthYear = computed(() => {
  if (!dateVal.value) return null
  return parseInt(dateVal.value.split('-')[0])
})

const orderedJieqi = computed(() => {
  if (!jieqi.value) return null
  const idx = jieqi.value.findIndex(item => item.name === '冬至')
  if (idx === -1) return jieqi.value
  return [...jieqi.value.slice(idx), ...jieqi.value.slice(0, idx)]
})

const seasonMap = {
  '立春':'spring','雨水':'spring','惊蛰':'spring','春分':'spring','清明':'spring','谷雨':'spring',
  '立夏':'summer','小满':'summer','芒种':'summer','夏至':'summer','小暑':'summer','大暑':'summer',
  '立秋':'autumn','处暑':'autumn','白露':'autumn','秋分':'autumn','寒露':'autumn','霜降':'autumn',
  '立冬':'winter','小雪':'winter','大雪':'winter','冬至':'winter','小寒':'winter','大寒':'winter',
}
function getSeason(name) { return seasonMap[name] || 'spring' }

async function fetchJieqi(year) {
  if (jieqiCache[year]) {
    jieqi.value = jieqiCache[year]
    return
  }
  jieqiLoading.value = true
  try {
    const res = await fetch(`/api/jieqi/${year}`)
    const data = await res.json()
    const filtered = data.filter(item => !item.error)
    jieqiCache[year] = filtered
    jieqi.value = filtered
  } catch { jieqi.value = null }
  finally { jieqiLoading.value = false }
}

watch(result, (val) => {
  if (val && birthYear.value) fetchJieqi(birthYear.value)
  else jieqi.value = null
})

async function submit() {
  if (!dateVal.value) return
  loading.value = true; error.value = ''; result.value = null; jieqi.value = null
  const datetime = `${dateVal.value} ${timeVal.value}:00`
  try {
    const res = await fetch('/api/birthday', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: datetime }),
    })
    const data = await res.json()
    if (data.error) error.value = data.error
    else result.value = data
  } catch { error.value = '请求失败，请确认后端服务已启动' }
  finally { loading.value = false }
}

const theme = ref('dark')
function applyTheme() {
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}
function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  applyTheme()
}
onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved) theme.value = saved
  else if (window.matchMedia('(prefers-color-scheme: light)').matches) theme.value = 'light'
  applyTheme()
})
</script>

<template>
  <div class="app-shell" :class="{ 'has-result': hasResult }">
    <div class="query-card">
      <div class="query-inner">
        <button class="icon-wrap" @click="toggleTheme" :title="theme === 'dark' ? '切换亮色' : '切换暗色'">
          <svg v-if="theme === 'dark'" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>
          </svg>
        </button>

        <h1 class="title">生辰推算</h1>
        <p class="subtitle">输入公历生日，推算农历、岁名与天文时刻</p>

        <div class="picker-row">
          <DatePicker v-model="dateVal" />
          <TimePicker v-model="timeVal" />
        </div>

        <button class="submit-btn" :disabled="loading || !dateVal" @click="submit">
          <template v-if="loading">
            <span class="spinner"></span> 计算中...
          </template>
          <template v-else>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            查询
          </template>
        </button>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </div>

    <div v-if="result" class="results">
      <div class="taisui-hero">
        <div class="taisui-chars">
          <span v-for="(c, i) in result.taisui_name" :key="i" class="taisui-char">{{ c }}</span>
        </div>
        <p class="taisui-label">岁 名</p>
      </div>

      <div class="metrics-row">
        <div class="metric-card">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="metric-icon">
            <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
          </svg>
          <span class="metric-value">{{ result.lunar_birthday }}</span>
          <span class="metric-label">农历生日</span>
        </div>
        <div class="metric-card">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="metric-icon">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span class="metric-value">{{ result.solar_birthday.slice(0, 10) }}</span>
          <span class="metric-label">公历生日</span>
        </div>
        <div class="metric-card">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="metric-icon">
            <circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
          </svg>
          <span class="metric-value">{{ result.sun_longitude }}°</span>
          <span class="metric-label">太阳黄经</span>
        </div>
      </div>

      <div class="detail-cards">
        <div class="detail-card">
          <div class="detail-head">
            <span class="detail-dot"></span>岁首
          </div>
          <p class="detail-desc">{{ result.year_desc }}</p>
          <div class="detail-item">
            <span>合朔</span>
            <span class="detail-val">{{ result.lunar_conjunction }}</span>
          </div>
          <div class="detail-item">
            <span>冬至</span>
            <span class="detail-val">{{ result.winter_solstice }}</span>
          </div>
        </div>

        <div class="detail-card">
          <div class="detail-head">
            <span class="detail-dot"></span>出生
          </div>
          <p class="detail-desc">{{ result.month_desc }}</p>
          <div class="detail-item">
            <span>合朔</span>
            <span class="detail-val">{{ result.lunar_conjunction_birthday }}</span>
          </div>
          <div class="detail-item">
            <span>生日</span>
            <span class="detail-val">{{ result.solar_birthday }}</span>
          </div>
        </div>
      </div>

      <div v-if="jieqiLoading" class="jieqi-loading">加载节气数据...</div>
      <div v-else-if="orderedJieqi" class="jieqi-section">
        <div class="jieqi-head">{{ birthYear }}年节气</div>
        <div class="jieqi-grid">
          <div v-for="item in orderedJieqi" :key="item.name" class="jieqi-item" :class="getSeason(item.name)">
            <span class="jieqi-name">{{ item.name }}</span>
            <span class="jieqi-date">{{ item.datetime.slice(5, 16) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ========== base ========== */
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  transition: padding 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.app-shell.has-result {
  justify-content: flex-start;
  padding-top: 40px;
}
.query-card { width: 100%; max-width: 440px; }

.results {
  width: 100%; max-width: 440px;
  display: flex; flex-direction: column; gap: 10px;
  padding-bottom: 48px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== query ========== */
.query-inner {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 20px; padding: 36px 32px 32px; text-align: center;
}
.icon-wrap {
  display: inline-flex; padding: 14px;
  background: var(--primary-light); border-radius: 50%; margin-bottom: 16px;
  border: none; cursor: pointer; color: var(--primary);
  transition: all 0.2s;
}
.icon-wrap:hover { background: var(--primary); color: #fff; }
.title { font-size: 1.4rem; font-weight: 700; color: var(--text); letter-spacing: 0.04em; margin-bottom: 6px; }
.subtitle { color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 28px; }
.picker-row { display: flex; gap: 10px; margin-bottom: 18px; }
.picker-row > * { flex: 1; min-width: 0; }

.submit-btn {
  width: 100%; padding: 14px;
  background: var(--primary); color: #fff;
  border: none; border-radius: 12px;
  font-size: 0.95rem; font-weight: 600; font-family: inherit;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  gap: 8px; transition: all 0.2s;
}
.submit-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  box-shadow: 0 4px 24px var(--primary-glow);
}
.submit-btn:active:not(:disabled) { transform: scale(0.97); }
.submit-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-msg { color: #f87171; text-align: center; margin-top: 14px; font-size: 0.875rem; }

/* ========== taisui hero ========== */
.taisui-hero {
  position: relative;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 24px; padding: 48px 24px 40px;
  text-align: center; overflow: hidden;
}
.taisui-hero::before {
  content: '';
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 260px; height: 260px;
  background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
  pointer-events: none;
}
.taisui-hero::after {
  content: '';
  position: absolute;
  width: 3px; height: 3px; border-radius: 50%;
  background: var(--primary); opacity: 0.35;
  top: 22%; left: 18%;
  box-shadow:
    70px 15px 0 var(--primary),
    160px -8px 0 var(--accent),
    250px 20px 0 var(--primary),
    40px 70px 0 var(--accent),
    130px 80px 0 var(--primary),
    220px 65px 0 var(--accent),
    310px 60px 0 var(--primary),
    90px 40px 0 var(--accent),
    180px 50px 0 var(--primary),
    270px 35px 0 var(--accent);
}

.taisui-chars {
  display: flex; justify-content: center; gap: 14px;
  position: relative; z-index: 1;
}
.taisui-char {
  font-size: 3rem; font-weight: 700; letter-spacing: 0.05em;
  background: linear-gradient(180deg, var(--text) 20%, var(--primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 16px var(--primary-glow));
}
.taisui-label {
  position: relative; z-index: 1;
  margin-top: 16px;
  font-size: 0.72rem; color: var(--text-secondary);
  letter-spacing: 0.2em;
}

/* ========== metrics ========== */
.metrics-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
}
.metric-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 20px 12px;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.metric-icon { color: var(--primary); opacity: 0.6; }
.metric-value {
  font-size: 1.15rem; font-weight: 700; color: var(--text);
  text-align: center; word-break: break-all;
}
.metric-label {
  font-size: 0.7rem; color: var(--text-secondary);
  letter-spacing: 0.05em;
}

/* ========== detail cards ========== */
.detail-cards {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
.detail-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 22px;
}
.detail-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.78rem; font-weight: 600;
  color: var(--primary); letter-spacing: 0.06em;
  margin-bottom: 14px;
}
.detail-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--primary);
}
.detail-desc {
  font-size: 0.88rem; color: var(--text); line-height: 1.7; margin-bottom: 16px;
}
.detail-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 9px 0; border-top: 1px solid var(--border);
  font-size: 0.82rem; color: var(--text-secondary);
}
.detail-val { color: var(--text); font-weight: 500; }

/* ========== jieqi ========== */
.jieqi-loading { text-align: center; color: var(--text-secondary); font-size: 0.85rem; padding: 24px; }
.jieqi-section {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 20px 22px;
}
.jieqi-head {
  font-size: 0.72rem; font-weight: 600; color: var(--primary);
  letter-spacing: 0.08em; margin-bottom: 12px;
}
.jieqi-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px;
}
.jieqi-item {
  padding: 9px 10px; border-radius: 8px; border-left: 3px solid;
  background: var(--input-bg);
}
.jieqi-item.spring  { border-color: #6b9a5a; }
.jieqi-item.summer  { border-color: #e06050; }
.jieqi-item.autumn  { border-color: #d4a040; }
.jieqi-item.winter  { border-color: #6b8db5; }
.jieqi-name { font-size: 0.8rem; font-weight: 600; color: var(--text); display: block; line-height: 1.3; }
.jieqi-date { font-size: 0.68rem; color: var(--text-secondary); display: block; margin-top: 1px; }

/* ========== mobile ========== */
@media (max-width: 480px) {
  .query-inner { padding: 28px 20px 24px; }
  .taisui-hero { padding: 36px 16px 32px; }
  .taisui-char { font-size: 2.4rem; }
  .metrics-row { grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .metric-card { padding: 16px 8px; }
  .metric-value { font-size: 1rem; }
  .detail-cards { grid-template-columns: 1fr; }
  .jieqi-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ========== desktop ========== */
@media (min-width: 768px) {
  .app-shell { padding: 40px 32px; }
  .app-shell:not(.has-result) .query-card { max-width: 480px; }

  .app-shell.has-result {
    display: grid;
    grid-template-columns: 320px minmax(0, 1fr);
    gap: 28px;
    max-width: 1100px; margin: 0 auto;
    align-items: start; justify-content: unset;
  }
  .app-shell.has-result .query-card { position: sticky; top: 40px; max-width: none; }
  .app-shell.has-result .picker-row { flex-direction: column; }
  .app-shell.has-result .results { max-width: none; padding-bottom: 64px; }

  .taisui-hero { padding: 56px 32px 48px; }
  .taisui-hero::before { width: 340px; height: 340px; }
  .taisui-char { font-size: 3.6rem; }

  .jieqi-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 1100px) {
  .app-shell.has-result {
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 36px;
  }
  .taisui-char { font-size: 4rem; }
  .jieqi-grid { grid-template-columns: repeat(6, 1fr); }
}
</style>
