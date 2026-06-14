<script setup lang="ts">
import { ref } from "vue"
import FretBoard from "./components/FretBoard.vue"

const message = ref("GuitarTab AI")
const subtitle = ref("上传音频，AI 自动生成吉他六线谱")
const uploadedFile = ref<File | null>(null)
const uploadResult = ref("")
const tabNotes = ref<any[]>([])
const tabText = ref("")
const mode = ref<"ai" | "mock" | "">("")
const fileName = ref("")

function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadedFile.value = input.files[0]
    uploadResult.value = ""
    tabText.value = ""
    tabNotes.value = []
    mode.value = ""
    fileName.value = input.files[0].name
  }
}

async function uploadFile() {
  if (!uploadedFile.value) return

  const formData = new FormData()
  formData.append("file", uploadedFile.value)

  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  })

  const data = await response.json()

  console.log("=== 后端返回数据 ===")
  console.log("文件名:", data.filename)
  console.log("模式:", data.mode)
  console.log("tab_text:", data.tab_text)
  console.log("音符列表:", data.notes)

  uploadResult.value = `${data.filename} (${data.size_bytes} 字节)`
  mode.value = data.mode?.includes("ai") ? "ai" : "mock"
  tabNotes.value = data.notes || []
  tabText.value = data.tab_text || ""
}
</script>

<template>
  <div class="app-container">
    <!-- 顶部品牌区 -->
    <header class="brand">
      <div class="brand-icon">🎸</div>
      <h1>{{ message }}</h1>
      <p class="brand-sub">{{ subtitle }}</p>
    </header>

    <!-- 上传卡片 -->
    <section class="card upload-card">
      <div class="upload-row">
        <label class="file-drop" for="audio-file">
          <span v-if="!fileName">点击选择音频文件</span>
          <span v-else class="file-name">{{ fileName }}</span>
        </label>
        <input id="audio-file" type="file" accept="audio/*" @change="onFileSelected" />
        <button class="btn-primary" :disabled="!uploadedFile" @click="uploadFile">
          解析音频
        </button>
      </div>
    </section>

    <!-- 模式标签 -->
    <div v-if="mode" class="mode-pill" :class="mode">
      <span class="mode-dot"></span>
      {{ mode === "ai" ? "AI 模式" : "模拟模式" }}
    </div>

    <!-- 结果区域 — 六线谱 + 指板 + 数据 依次排列 -->
    <div v-if="tabNotes.length > 0" class="results">

      <!-- 六线谱文本 -->
      <section class="card" v-if="tabText">
        <div class="card-label">六线谱</div>
        <pre class="tab-view">{{ tabText }}</pre>
      </section>

      <!-- 指板图 -->
      <section class="card fretboard-card">
        <div class="card-label">指板位置</div>
        <FretBoard :notes="tabNotes" />
      </section>

      <!-- 数据表格 -->
      <section class="card">
        <div class="card-label">音符数据</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>弦号</th>
              <th>品位</th>
              <th>音符</th>
              <th>开始</th>
              <th>结束</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(note, i) in tabNotes" :key="i">
              <td>{{ note.string ?? "?" }}弦</td>
              <td>{{ note.fret ?? "?" }}品</td>
              <td>{{ note.pitch }}</td>
              <td>{{ note.start_time }}s</td>
              <td>{{ note.end_time }}s</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>

    <!-- 结果文件信息 -->
    <p v-if="uploadResult && tabNotes.length === 0" class="result-text">{{ uploadResult }}</p>

    <!-- 页脚 -->
    <footer class="footer">
      GuitarTab AI — 用 AI 帮你扒谱
    </footer>
  </div>
</template>

<style>
/* 全局重置 */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #f8fafc;
  color: #1e293b;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}
</style>

<style scoped>
.app-container {
  max-width: 760px;
  margin: 0 auto;
  padding: 48px 20px 60px;
}

/* ---- 品牌 ---- */
.brand {
  text-align: center;
  margin-bottom: 44px;
}
.brand-icon {
  font-size: 2rem;
  margin-bottom: 6px;
}
.brand h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2px;
}
.brand-sub {
  font-size: 0.85rem;
  color: #64748b;
}

/* ---- 卡片 ---- */
.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 22px 24px;
  margin-bottom: 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.card-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 14px;
}

/* ---- 上传区 ---- */
.upload-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.upload-row input[type="file"] {
  display: none;
}
.file-drop {
  flex: 1;
  padding: 12px 16px;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.85rem;
  color: #94a3b8;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  text-align: center;
}
.file-drop:hover {
  border-color: #2563eb;
  background: #eff6ff;
}
.file-drop .file-name {
  color: #1e293b;
  font-weight: 500;
}

.btn-primary {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}
.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* ---- 模式标签 ---- */
.mode-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 8px;
}
.mode-pill .mode-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.mode-pill.ai {
  background: #dbeafe;
  color: #1e40af;
}
.mode-pill.ai .mode-dot {
  background: #2563eb;
}
.mode-pill.mock {
  background: #fef3c7;
  color: #92400e;
}
.mode-pill.mock .mode-dot {
  background: #f59e0b;
}

/* ---- 六线谱文本 ---- */
.tab-view {
  background: #0f172a;
  border-radius: 10px;
  padding: 22px 20px;
  font-family: "SF Mono", "Cascadia Code", "Consolas", monospace;
  font-size: 0.82rem;
  line-height: 2;
  color: #e2e8f0;
  overflow-x: auto;
  white-space: pre;
}

/* ---- 指板图 ---- */
.fretboard-card {
  background: #faf5eb;
}

/* ---- 数据表格 ---- */
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.8rem;
}
.data-table th {
  background: #f1f5f9;
  color: #475569;
  padding: 10px 14px;
  text-align: center;
  font-weight: 600;
  font-size: 0.7rem;
  letter-spacing: 1px;
}
.data-table th:first-child {
  border-radius: 8px 0 0 0;
}
.data-table th:last-child {
  border-radius: 0 8px 0 0;
}
.data-table td {
  padding: 9px 14px;
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}
.data-table tr:last-child td:first-child {
  border-radius: 0 0 0 8px;
}
.data-table tr:last-child td:last-child {
  border-radius: 0 0 8px 0;
}
.data-table tbody tr:hover td {
  background: #f8fafc;
}

/* ---- 结果 & 页脚 ---- */
.result-text {
  text-align: center;
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 8px;
}

.footer {
  text-align: center;
  margin-top: 40px;
  font-size: 0.75rem;
  color: #94a3b8;
}
</style>
