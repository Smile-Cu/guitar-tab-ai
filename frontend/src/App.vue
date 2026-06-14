<script setup lang="ts">
import { ref } from "vue"

// 页面状态 —— ref() 是响应式数据，值变了页面自动刷新
const message = ref("GuitarTab AI - 电吉他 AI 辅助扒谱工具")
const uploadedFile = ref<File | null>(null)
const uploadResult = ref("")
const tabNotes = ref<any[]>([])   // 六线谱数据：弦号、品位、音高、时间
const tabText = ref("")           // ASCII 六线谱文本（后端 format_tab_string 的输出）

// 文件选择
function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadedFile.value = input.files[0]
    uploadResult.value = ""
    tabText.value = ""
    tabNotes.value = []
  }
}

// 上传音频并解析结果
async function uploadFile() {
  if (!uploadedFile.value) return

  const formData = new FormData()
  formData.append("file", uploadedFile.value)

  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  })

  const data = await response.json()

  // 打印完整返回数据到控制台 —— 打开 F12 Console 标签就能看到
  console.log("=== 后端返回数据 ===")
  console.log("文件名:", data.filename)
  console.log("模式:", data.mode)
  console.log("tab_text:", data.tab_text)
  console.log("音符列表:", data.notes)

  uploadResult.value = `${data.filename} (${data.size_bytes} 字节) · ${data.mode} 模式`
  tabNotes.value = data.notes || []
  tabText.value = data.tab_text || ""
}
</script>

<template>
  <div class="app">
    <h1>{{ message }}</h1>

    <div class="upload-section">
      <input type="file" accept="audio/*" @change="onFileSelected" />
      <button @click="uploadFile" :disabled="!uploadedFile">上传音频</button>
    </div>

    <p v-if="uploadResult" class="result">{{ uploadResult }}</p>

    <!-- 六线谱 ASCII 文本可视化 -->
    <pre v-if="tabText" class="tab-display">{{ tabText }}</pre>

    <!-- 六线谱数据表格 -->
    <table v-if="tabNotes.length > 0" class="tab-table">
      <thead>
        <tr>
          <th>弦号</th>
          <th>品位</th>
          <th>MIDI 音高</th>
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

    <p v-if="tabNotes.length > 0" class="hint">
      按下 F12 → Console 标签可以看到后端返回的完整数据
    </p>
  </div>
</template>

<style scoped>
.app {
  max-width: 700px;
  margin: 40px auto;
  font-family: system-ui, sans-serif;
}

h1 {
  font-size: 1.4rem;
  color: #222;
  text-align: center;
}

.upload-section {
  margin: 20px 0;
  display: flex;
  gap: 10px;
  justify-content: center;
}

button {
  padding: 8px 20px;
  cursor: pointer;
}

.result {
  color: #4a7c59;
  text-align: center;
}

.tab-table {
  width: 100%;
  margin-top: 20px;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tab-table th,
.tab-table td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: center;
}

.tab-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.tab-table tbody tr:hover {
  background: #f9f9f9;
}

.hint {
  margin-top: 12px;
  font-size: 0.8rem;
  color: #999;
  text-align: center;
}

/* 六线谱 ASCII 文本展示块 */
.tab-display {
  margin-top: 24px;
  padding: 20px 24px;
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: "Courier New", "Consolas", monospace;
  font-size: 0.95rem;
  line-height: 1.8;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre;
  letter-spacing: 0;
}
</style>
