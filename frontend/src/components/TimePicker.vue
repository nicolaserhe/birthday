<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const draftHour = ref(null)
const draftMin = ref(null)
const draftPM = ref(false)

const clockHours = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
const clockMinutes = Array.from({ length: 12 }, (_, i) => i * 5)

const displayTime = computed(() => props.modelValue || '--:--')

const draftDisplay = computed(() => {
  if (draftHour.value === null) return '--:--'
  return `${String(draftHour.value).padStart(2, '0')}:${String(draftMin.value).padStart(2, '0')}`
})

function initDraft() {
  if (props.modelValue) {
    let h = parseInt(props.modelValue.split(':')[0])
    draftMin.value = parseInt(props.modelValue.split(':')[1])
    draftPM.value = h >= 12
    h = h % 12
    draftHour.value = h === 0 ? 12 : h
  } else {
    const now = new Date()
    let h = now.getHours()
    draftMin.value = Math.floor(now.getMinutes() / 5) * 5
    draftPM.value = h >= 12
    h = h % 12
    draftHour.value = h === 0 ? 12 : h
  }
}

function selectHour(clockH) { draftHour.value = clockH }
function selectMinute(m) { draftMin.value = m }
function togglePM(pm) { draftPM.value = pm }

function isHourActive(clockH) { return clockH === draftHour.value }
function isMinActive(m) { return m === draftMin.value }

function confirm() {
  let h = draftHour.value === 12 ? 0 : draftHour.value
  if (draftPM.value) h += 12
  emit('update:modelValue', `${String(h).padStart(2, '0')}:${String(draftMin.value).padStart(2, '0')}`)
  open.value = false
}

function cancel() { open.value = false }

function toggle() { initDraft(); open.value = !open.value }

function markerPos(i, r) {
  const angle = (i * 30 - 90) * Math.PI / 180
  const x = Math.cos(angle) * r
  const y = Math.sin(angle) * r
  return { left: `calc(50% + ${Math.round(x)}px)`, top: `calc(50% + ${Math.round(y)}px)` }
}
</script>

<template>
  <div class="cf-root">
    <button class="cf-trigger" @click="toggle">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
      </svg>
      <span>{{ displayTime }}</span>
    </button>

    <Teleport to="body">
      <div v-if="open" class="cf-overlay" @click="cancel" />
      <div v-if="open" class="cf-dropdown">
        <div class="cf-face">
          <button
            v-for="(h, i) in clockHours" :key="'h'+h"
            class="cf-hour" :class="{ active: isHourActive(h) }"
            :style="markerPos(i, 102)" @click="selectHour(h)"
          >{{ h }}</button>

          <button
            v-for="(m, i) in clockMinutes" :key="'m'+m"
            class="cf-min" :class="{ active: isMinActive(m) }"
            :style="markerPos(i, 66)" @click="selectMinute(m)"
          >{{ String(m).padStart(2, '0') }}</button>

          <div class="cf-center">{{ draftDisplay }}</div>
        </div>

        <div class="cf-ampm">
          <button :class="{ active: !draftPM }" @click="togglePM(false)">上午</button>
          <button :class="{ active: draftPM }" @click="togglePM(true)">下午</button>
        </div>

        <div class="cf-actions">
          <button class="cf-cancel" @click="cancel">取消</button>
          <button class="cf-confirm" @click="confirm">确认</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.cf-root { position: relative; width: 100%; }

.cf-trigger {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 13px 15px;
  font-size: 0.95rem; font-family: inherit;
  color: var(--text); background: var(--input-bg);
  border: 1px solid var(--border); border-radius: 12px;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.cf-trigger:hover { border-color: var(--primary); background: var(--primary-light); }
.cf-trigger svg { color: var(--text-secondary); flex-shrink: 0; }

.cf-overlay {
  position: fixed; inset: 0; z-index: 99;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
}

.cf-dropdown {
  position: fixed; z-index: 100;
  top: 50%; left: 50%; transform: translate(-50%, -50%);
  background: var(--card); border: 1px solid var(--border);
  border-radius: 24px; padding: 32px 28px 22px;
  width: 320px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.4);
  animation: cfIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cfIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.94); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.cf-face {
  width: 264px; height: 264px;
  border-radius: 50%; position: relative; margin: 0 auto;
  background: var(--input-bg);
  border: 1px solid var(--border);
  box-shadow: inset 0 0 60px rgba(129, 140, 248, 0.03);
}

.cf-hour,
.cf-min {
  position: absolute;
  transform: translate(-50%, -50%);
  border: none; background: transparent;
  font-family: inherit; cursor: pointer;
  transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
  line-height: 1; color: var(--text-secondary);
  border-radius: 50%;
}

.cf-hour {
  width: 36px; height: 36px;
  font-size: 1rem; font-weight: 500;
}
.cf-hour:hover { background: var(--primary-light); color: var(--text); }
.cf-hour.active { background: var(--primary); color: #fff; font-weight: 600; }

.cf-min {
  width: 30px; height: 30px;
  font-size: 0.7rem; font-weight: 500;
}
.cf-min:hover { background: var(--primary-light); color: var(--text); }
.cf-min.active { background: var(--primary); color: #fff; font-weight: 600; }

.cf-center {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; font-weight: 600; color: var(--text);
  letter-spacing: 0.04em;
  pointer-events: none;
}

.cf-ampm {
  display: flex; gap: 8px; margin-top: 18px;
  justify-content: center;
}

.cf-ampm button {
  padding: 8px 24px; border: 1px solid var(--border);
  background: transparent; color: var(--text-secondary);
  border-radius: 10px; font-size: 0.85rem; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}

.cf-ampm button:hover { border-color: var(--primary); color: var(--text); }
.cf-ampm button.active { background: var(--primary); border-color: var(--primary); color: #fff; }

.cf-actions {
  display: flex; gap: 10px; margin-top: 16px;
}
.cf-cancel,
.cf-confirm {
  flex: 1; padding: 10px;
  border-radius: 10px; font-size: 0.9rem; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.cf-cancel {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-secondary);
}
.cf-cancel:hover { border-color: var(--text-secondary); color: var(--text); }
.cf-confirm {
  background: var(--primary); border: none;
  color: #fff; font-weight: 600;
}
.cf-confirm:hover { background: var(--primary-hover); }
</style>
