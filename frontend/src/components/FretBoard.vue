<script setup lang="ts">
/**
 * FretBoard — 吉他指板可视化组件
 *
 * 接收已转换的 tab 音符数据，用 SVG 渲染出：
 * - 6 根弦（从粗到细：E A D G B e）
 * - 品位线 + 品位标记点（3/5/7/9/12 品）
 * - 音符位置圆点（带有音名标签）
 */
import { computed } from "vue"

const props = defineProps<{
  notes: any[]
}>()

const STRING_LABELS = ["e", "B", "G", "D", "A", "E"]
const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
const FRET_MARKERS = [3, 5, 7, 9, 12, 15, 17]

function midiToName(pitch: number) {
  return `${NOTE_NAMES[pitch % 12]}${Math.floor(pitch / 12) - 1}`
}

const fretRange = computed(() => {
  const valid = props.notes.filter(n => n.string && n.fret != null)
  if (valid.length === 0) return { start: 0, end: 5 }
  const frets = valid.map(n => n.fret)
  let min = Math.max(0, Math.min(...frets) - 1)
  let max = Math.min(19, Math.max(...frets) + 2)
  while (max - min < 5 && max < 19) max++
  while (max - min < 5 && min > 0) min--
  return { start: min, end: max }
})

const visibleFrets = computed(() => {
  const { start, end } = fretRange.value
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const svgHeight = 200
const svgWidth = computed(() => visibleFrets.value.length * 50 + 60)
const topPad = 16
const bottomPad = 20
const leftPad = 40
const stringSpacing = 28
const drawWidth = computed(() => svgWidth.value - leftPad - 20)

function noteCoords(note: any) {
  const s = note.string
  const f = note.fret
  if (s == null || f == null) return null
  const fretIdx = f - fretRange.value.start
  const x = leftPad + (fretIdx / (visibleFrets.value.length - 1)) * drawWidth.value
  const y = topPad + (s - 1) * stringSpacing
  return { x, y, s, f }
}

const noteDots = computed(() => {
  return props.notes
    .filter(n => n.string && n.fret != null)
    .map(n => ({
      ...noteCoords(n)!,
      pitch: n.pitch,
      name: n.pitch != null ? midiToName(n.pitch) : "?"
    }))
})

const uniqueDots = computed(() => {
  const seen = new Set<string>()
  return noteDots.value.filter(d => {
    const key = `${d.s}-${d.f}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})
</script>

<template>
  <div class="fretboard-wrap">
    <svg
      :width="svgWidth"
      :height="svgHeight"
      :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
      class="fretboard-svg"
    >
      <!-- 背景 -->
      <rect :width="svgWidth" :height="svgHeight" fill="transparent" rx="4" />

      <!-- 品位竖线 -->
      <line
        v-for="(fret, fi) in visibleFrets"
        :key="'fret-' + fret"
        :x1="leftPad + (fi / (visibleFrets.length - 1)) * drawWidth"
        :y1="topPad"
        :x2="leftPad + (fi / (visibleFrets.length - 1)) * drawWidth"
        :y2="topPad + 5 * stringSpacing"
        :stroke="fret === 0 ? '#c5a880' : '#e2d5c3'"
        :stroke-width="fret === 0 ? 2.5 : 1"
      />

      <!-- 品位标记点 -->
      <circle
        v-if="FRET_MARKERS.includes(fret) && fi > 0"
        v-for="(fret, fi) in visibleFrets"
        :key="'marker-' + fret"
        :cx="leftPad + ((fi - 0.5) / (visibleFrets.length - 1)) * drawWidth"
        :cy="topPad + 2.5 * stringSpacing"
        r="4"
        fill="#c5a880"
      />

      <!-- 琴弦 -->
      <line
        v-for="si in 6"
        :key="'string-' + si"
        :x1="leftPad"
        :y1="topPad + (si - 1) * stringSpacing"
        :x2="leftPad + drawWidth"
        :y2="topPad + (si - 1) * stringSpacing"
        :stroke="si >= 5 ? '#94a3b8' : '#64748b'"
        :stroke-width="7 - si * 0.5"
        stroke-linecap="round"
      />

      <!-- 弦标签 -->
      <text
        v-for="si in 6"
        :key="'label-' + si"
        :x="12"
        :y="topPad + (si - 1) * stringSpacing + 5"
        :font-size="si === 1 ? 10 : 11"
        :font-weight="si === 6 ? 'bold' : 'normal'"
        fill="#475569"
        text-anchor="middle"
      >{{ STRING_LABELS[si - 1] }}</text>

      <!-- 品位数字 -->
      <text
        v-for="(fret, fi) in visibleFrets"
        :key="'fnum-' + fret"
        :x="leftPad + (fi / (visibleFrets.length - 1)) * drawWidth"
        :y="topPad + 5 * stringSpacing + 16"
        font-size="9"
        fill="#94a3b8"
        text-anchor="middle"
      >{{ fret }}</text>

      <!-- 音符圆点 -->
      <g v-for="(dot, di) in uniqueDots" :key="'dot-' + di">
        <circle
          :cx="dot.x"
          :cy="dot.y"
          r="11"
          fill="#2563eb"
          stroke="#1d4ed8"
          stroke-width="1.5"
          opacity="0.92"
        />
        <text
          :x="dot.x"
          :y="dot.y + 4"
          font-size="9"
          fill="white"
          font-weight="600"
          text-anchor="middle"
        >{{ dot.name }}</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.fretboard-wrap {
  padding: 4px 0;
}
.fretboard-svg {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  border-radius: 6px;
}
</style>
