<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const mode = ref('calendar')
const viewYear = ref(new Date().getFullYear())
const viewMonth = ref(new Date().getMonth() + 1)
const decadeStart = ref(Math.floor(viewYear.value / 10) * 10)

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
})

const display = computed(() => {
  if (!props.modelValue) return '选择日期'
  const [y, m, d] = props.modelValue.split('-')
  return `${y}年${parseInt(m)}月${parseInt(d)}日`
})

const thisYear = new Date().getFullYear()

const days = computed(() => {
  const first = new Date(viewYear.value, viewMonth.value - 1, 1)
  const startPad = first.getDay()
  const daysInMonth = new Date(viewYear.value, viewMonth.value, 0).getDate()
  const result = []
  for (let i = 0; i < startPad; i++) {
    result.push({ date: '', inMonth: false, key: `pad-${i}` })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${viewYear.value}-${String(viewMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push({ date: d, inMonth: true, dateStr, key: dateStr })
  }
  while (result.length < 42) {
    result.push({ date: '', inMonth: false, key: `pad-${result.length}` })
  }
  return result
})

const yearRange = computed(() => {
  const s = decadeStart.value
  return Array.from({ length: 12 }, (_, i) => s + i)
})

function select(day) {
  if (!day.inMonth) return
  emit('update:modelValue', day.dateStr)
  open.value = false
}

function prevMonth() {
  if (viewMonth.value === 1) { viewYear.value--; viewMonth.value = 12 }
  else viewMonth.value--
}

function nextMonth() {
  if (viewMonth.value === 12) { viewYear.value++; viewMonth.value = 1 }
  else viewMonth.value++
}

function prevYear() { viewYear.value-- }
function nextYear() { viewYear.value++ }

function enterYearMode() {
  decadeStart.value = Math.floor(viewYear.value / 10) * 10
  mode.value = 'year'
}

function enterMonthMode() { mode.value = 'month' }

function selectYear(y) {
  viewYear.value = y
  mode.value = 'calendar'
}

function selectMonth(m) {
  viewMonth.value = m
  mode.value = 'calendar'
}

function prevDecade() { decadeStart.value -= 12 }
function nextDecade() { decadeStart.value += 12 }

function toggle() {
  mode.value = 'calendar'
  open.value = !open.value
}
</script>

<template>
  <div class="dp-root">
    <button class="dp-trigger" @click="toggle">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <span :class="{ placeholder: !modelValue }">{{ display }}</span>
    </button>

    <Teleport to="body">
      <div v-if="open" class="dp-overlay" @click="open = false" />
      <div v-if="open" class="dp-dropdown">

        <!-- month picker -->
        <template v-if="mode === 'month'">
          <div class="dp-header year-header">
            <button class="dp-nav" @click="prevYear">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="dp-title">{{ viewYear }}年</span>
            <button class="dp-nav" @click="nextYear">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <div class="dp-month-grid">
            <button
              v-for="m in 12" :key="m"
              class="dp-month-cell"
              :class="{ active: m === viewMonth }"
              @click="selectMonth(m)"
            >{{ m }}月</button>
          </div>
        </template>

        <!-- year picker -->
        <template v-else-if="mode === 'year'">
          <div class="dp-header year-header">
            <button class="dp-nav" @click="prevDecade">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="dp-title">{{ decadeStart }} — {{ decadeStart + 11 }}</span>
            <button class="dp-nav" @click="nextDecade" :disabled="decadeStart + 12 > thisYear + 1">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <div class="dp-year-grid">
            <button
              v-for="y in yearRange" :key="y"
              class="dp-year-cell"
              :class="{
                active: y === viewYear,
                current: y === thisYear,
              }"
              :disabled="y > thisYear + 1"
              @click="selectYear(y)"
            >{{ y }}</button>
          </div>
        </template>

        <!-- calendar -->
        <template v-else>
          <div class="dp-header">
            <button class="dp-nav dp-nav-sm" @click="prevYear">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/></svg>
            </button>
            <button class="dp-nav" @click="prevMonth">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="dp-title">
              <button class="dp-year-btn" @click="enterYearMode">{{ viewYear }}年</button><button class="dp-year-btn" @click="enterMonthMode">{{ viewMonth }}月</button>
            </span>
            <button class="dp-nav" @click="nextMonth">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
            <button class="dp-nav dp-nav-sm" @click="nextYear">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 17 18 12 13 7"/><polyline points="6 17 11 12 6 7"/></svg>
            </button>
          </div>
          <div class="dp-weekdays">
            <span v-for="d in ['日','一','二','三','四','五','六']" :key="d">{{ d }}</span>
          </div>
          <div class="dp-grid">
            <button
              v-for="day in days"
              :key="day.key"
              class="dp-day"
              :class="{
                outside: !day.inMonth,
                selected: day.dateStr === modelValue,
                today: day.dateStr === today,
              }"
              :disabled="!day.inMonth"
              @click="select(day)"
            >{{ day.date }}</button>
          </div>
        </template>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.dp-root { position: relative; width: 100%; }

.dp-trigger {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 13px 15px;
  font-size: 0.95rem; font-family: inherit;
  color: var(--text); background: var(--input-bg);
  border: 1px solid var(--border); border-radius: 12px;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.dp-trigger:hover { border-color: var(--primary); background: var(--primary-light); }
.dp-trigger svg { color: var(--text-secondary); flex-shrink: 0; }
.dp-trigger .placeholder { color: #555; }

.dp-overlay {
  position: fixed; inset: 0; z-index: 99;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
}

.dp-dropdown {
  position: fixed; z-index: 100;
  top: 50%; left: 50%; transform: translate(-50%, -50%);
  background: var(--card); border: 1px solid var(--border);
  border-radius: 20px; padding: 24px; width: 312px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.4);
  animation: dpIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dpIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.94); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.dp-header {
  display: flex; align-items: center; justify-content: center;
  gap: 6px; margin-bottom: 16px;
}
.year-header { justify-content: space-between; }

.dp-title {
  font-size: 1.05rem; font-weight: 600; color: var(--text);
  letter-spacing: 0.02em; text-align: center; flex: 1; white-space: nowrap;
}

.dp-year-btn {
  border: none; background: transparent;
  font-size: inherit; font-weight: inherit; font-family: inherit;
  color: var(--primary); cursor: pointer; padding: 0;
  border-radius: 4px; transition: opacity 0.15s;
}
.dp-year-btn:hover { opacity: 0.75; }

.dp-nav {
  width: 34px; height: 34px; border: none;
  background: var(--input-bg); border-radius: 10px;
  cursor: pointer; display: flex; align-items: center;
  justify-content: center; color: var(--text-secondary);
  transition: all 0.15s; flex-shrink: 0;
}
.dp-nav:hover:not(:disabled) { background: var(--primary-light); color: var(--text); }
.dp-nav:disabled { opacity: 0.3; cursor: not-allowed; }
.dp-nav-sm { width: 28px; height: 28px; border-radius: 8px; }

.dp-weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr);
  text-align: center; margin-bottom: 4px;
}
.dp-weekdays span {
  font-size: 0.7rem; color: var(--text-secondary);
  font-weight: 500; padding: 4px 0;
}

.dp-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }

.dp-day {
  width: 100%; aspect-ratio: 1; border: none; background: transparent;
  border-radius: 10px; font-size: 0.9rem; font-family: inherit;
  cursor: pointer; color: var(--text); transition: all 0.12s;
  display: flex; align-items: center; justify-content: center;
}
.dp-day:hover:not(.outside):not(.selected) { background: var(--primary-light); }
.dp-day.outside { visibility: hidden; }
.dp-day.today { font-weight: 700; color: var(--primary); }
.dp-day.selected { background: var(--primary); color: #fff; font-weight: 600; }
.dp-day.selected.today { background: var(--primary); color: #fff; }

/* year grid */
.dp-year-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.dp-year-cell {
  padding: 14px 8px; border: none;
  background: var(--input-bg); border-radius: 10px;
  font-size: 0.92rem; font-family: inherit;
  cursor: pointer; color: var(--text); transition: all 0.12s;
  text-align: center;
}
.dp-year-cell:hover:not(:disabled) { background: var(--primary-light); }
.dp-year-cell.current { font-weight: 700; color: var(--primary); }
.dp-year-cell.active { background: var(--primary); color: #fff; font-weight: 600; }
.dp-year-cell.active.current { background: var(--primary); color: #fff; }
.dp-year-cell:disabled { opacity: 0.25; cursor: not-allowed; }

/* month grid */
.dp-month-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.dp-month-cell {
  padding: 16px 8px; border: none;
  background: var(--input-bg); border-radius: 10px;
  font-size: 0.95rem; font-family: inherit;
  cursor: pointer; color: var(--text); transition: all 0.12s;
  text-align: center;
}
.dp-month-cell:hover { background: var(--primary-light); }
.dp-month-cell.active { background: var(--primary); color: #fff; font-weight: 600; }
</style>
