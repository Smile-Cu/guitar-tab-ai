<script setup lang="ts">
// <script setup> 是 Vue 3 的简写写法，不需要写 return
// lang="ts" 表示这个文件用 TypeScript

import { ref } from 'vue'

// ref 是 Vue 的响应式数据——值变了，页面自动跟着变
const message = ref('GuitarTab AI - 电吉他 AI 辅助扒谱工具')
const uploadedFile = ref<File | null>(null)
const uploadResult = ref('')

// 处理文件选择：用户选完文件后，暂存到 uploadedFile 里
function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadedFile.value = input.files[0]
    uploadResult.value = ''
  }
}

// 上传文件到后端
async function uploadFile() {
  if (!uploadedFile.value) return

  const formData = new FormData()
  formData.append('file', uploadedFile.value)

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  })

  const data = await response.json()
  uploadResult.value = `收到: ${data.filename} (${data.size_bytes} 字节)`
}
</script>

<template>
  <div class="app">
    <h1>{{ message }}</h1>

    <!-- 文件上传区域 -->
    <div class="upload-section">
      <input
        type="file"
        accept="audio/*"
        @change="onFileSelected"
      />
      <button @click="uploadFile" :disabled="!uploadedFile">
        上传音频
      </button>
    </div>

    <!-- 显示上传结果 -->
    <p v-if="uploadResult" class="result">{{ uploadResult }}</p>
  </div>
</template>

<style scoped>
/* scoped 表示这里的样式只影响当前组件 */
.app {
  max-width: 700px;
  margin: 60px auto;
  font-family: system-ui, sans-serif;
  text-align: center;
}

h1 {
  font-size: 1.5rem;
  color: #222;
}

.upload-section {
  margin: 24px 0;
  display: flex;
  gap: 12px;
  justify-content: center;
}

button {
  padding: 8px 20px;
  cursor: pointer;
}

.result {
  color: #4a7c59;
}
</style>
