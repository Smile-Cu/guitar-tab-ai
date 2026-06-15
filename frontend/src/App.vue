<script setup lang="ts">
import { ref } from "vue"

const view = ref<"login" | "main">("login")
const isRegister = ref(false)
const token = ref("")
const username = ref("")
const authUser = ref("")
const authPass = ref("")
const authError = ref("")

const uploadedFile = ref<File | null>(null)
const fileName = ref("")
const loading = ref(false)
const statusText = ref("")
const downloadUrl = ref("")
const tabText = ref("")
const mode = ref("")
const noteCount = ref(0)

const savedTabs = ref<any[]>([])

async function doAuth() {
  authError.value = ""
  const url = isRegister.value ? "/api/register" : "/api/login"
  try {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: authUser.value, password: authPass.value }) })
    const d = await r.json()
    if (!r.ok) { authError.value = d.error || d.detail || "请求失败"; return }
    token.value = d.token; username.value = d.username; view.value = "main"; await loadTabs()
  } catch (e: any) { authError.value = "网络错误: " + e.message }
}

function logout() { token.value = ""; username.value = ""; view.value = "login"; savedTabs.value = []; tabText.value = ""; statusText.value = "" }

function onFileSelected(e: Event) {
  const inp = e.target as HTMLInputElement
  if (inp.files?.[0]) { uploadedFile.value = inp.files[0]; fileName.value = inp.files[0].name; statusText.value = ""; downloadUrl.value = ""; tabText.value = ""; mode.value = "" }
}

async function uploadFile() {
  if (!uploadedFile.value) return; loading.value = true
  const fd = new FormData(); fd.append("file", uploadedFile.value)
  try {
    const r = await fetch("/api/upload", { method: "POST", body: fd }); const d = await r.json()
    mode.value = d.mode?.includes("ai") ? "ai" : "mock"; noteCount.value = d.note_count || 0
    tabText.value = d.tab_text || ""; downloadUrl.value = d.download_url || ""
    statusText.value = d.filename + " - " + (d.note_count || 0) + " 个音符"
  } catch (e: any) { statusText.value = "出错: " + e.message } finally { loading.value = false }
}

async function loadTabs() {
  try { const r = await fetch("/api/tabs", { headers: { Authorization: "Bearer " + token.value } }); savedTabs.value = r.ok ? await r.json() : [] } catch { savedTabs.value = [] }
}

async function saveTab() {
  if (!tabText.value || !token.value) return
  await fetch("/api/tabs", { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + token.value }, body: JSON.stringify({ filename: fileName.value, tab_text: tabText.value, note_count: noteCount.value, mode: mode.value }) })
  await loadTabs()
}

async function loadTab(id) {
  try {
    const r = await fetch("/api/tabs/" + id, { headers: { Authorization: "Bearer " + token.value } })
    if (r.ok) {
      const t = await r.json()
      tabText.value = t.tab_text; fileName.value = t.filename
      noteCount.value = t.note_count; mode.value = t.mode
      statusText.value = t.filename + " - " + (t.note_count || 0) + " ??"
      downloadUrl.value = ""
    }
  } catch {}
}

async function deleteTab(id: number) {
  await fetch("/api/tabs/" + id, { method: "DELETE", headers: { Authorization: "Bearer " + token.value } })
  await loadTabs()
}
</script>

<template>
  <div v-if="view === 'login'" class="login-page">
    <div class="login-card">
      <div style="text-align:center;font-size:2rem;margin-bottom:8px;">🎸</div>
      <h2>{{ isRegister ? "注册" : "登录" }} GuitarTab AI</h2>
      <input v-model="authUser" placeholder="用户名" class="input" />
      <input v-model="authPass" type="password" placeholder="密码" class="input" />
      <p v-if="authError" style="color:#ef4444;font-size:0.8rem;text-align:center;">{{ authError }}</p>
      <button class="btn-auth" @click="doAuth">{{ isRegister ? "注册" : "登录" }}</button>
      <p style="text-align:center;font-size:0.8rem;color:#94a3b8;margin-top:12px;cursor:pointer;" @click="isRegister=!isRegister">{{ isRegister ? "已有账号？去登录" : "没有账号？去注册" }}</p>
    </div>
  </div>

  <div v-else class="main-layout">
    <!-- ====== 左侧谱库 ====== -->
    <aside class="sidebar">
      <div class="sidebar-head">
        <span style="font-size:1.2rem;">🎸</span>
        <span style="font-weight:700;font-size:0.95rem;">我的吉他谱</span>
        <span class="tab-count">{{ savedTabs.length }}</span>
      </div>
      <div v-if="savedTabs.length === 0" class="empty-list">还没有保存吉他谱</div>
      <div v-for="t in savedTabs" :key="t.id" class="tab-item" @click="loadTab(t.id)">
        <div class="tab-item-info">
          <div class="tab-item-name">{{ t.filename }}</div>
          <div class="tab-item-meta">{{ t.note_count }} 音符 · {{ t.created_at?.slice(0,10) }}</div>
        </div>
        <button class="btn-del" @click="deleteTab(t.id)">🗑</button>
      </div>
      <div class="sidebar-foot">
        <span class="user-name">{{ username }}</span>
        <button class="btn-logout" @click="logout">退出</button>
      </div>
    </aside>

    <!-- ====== 右侧主区域 ====== -->
    <main class="content">
      <header class="brand">
        <h1>GuitarTab AI</h1>
        <p class="brand-sub">上传音频，AI 自动识别音符，导出 MIDI 文件</p>
      </header>

      <section class="card">
        <div class="upload-row">
          <label class="file-drop" for="af">
            <span v-if="!fileName">点击选择音频文件</span>
            <span v-else class="fn">{{ fileName }}</span>
          </label>
          <input id="af" type="file" accept="audio/*" @change="onFileSelected" />
          <button class="btn-primary" :disabled="!uploadedFile || loading" @click="uploadFile">{{ loading ? "处理中..." : "生成六线谱" }}</button>
        </div>
      </section>

      <div v-if="mode" class="mode-tag" :class="mode.includes('ai') ? 'ai' : 'mock'">{{ mode.includes("ai") ? "AI 模式" : "模拟模式" }}</div>

      <div v-if="tabText">
        <section class="card tab-card">
          <div class="card-head">
            <span class="label">六线谱</span>
            <button class="btn-save" @click="saveTab">💾 保存到谱库</button>
          </div>
          <pre class="tab-view">{{ tabText }}</pre>
        </section>

        <section v-if="downloadUrl" class="card result-card">
          <p class="rs">{{ statusText }}</p>
          <a :href="downloadUrl" class="btn-download" download>⬇ 下载 MIDI (.mid)</a>
        </section>
      </div>
    </main>
  </div>
</template>

<style>
*,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }
body { background:#f0f2f5; color:#1e293b; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
</style>

<style scoped>
/* Login */
.login-page { display:flex; justify-content:center; align-items:center; min-height:100vh; background:linear-gradient(135deg,#1e293b 0%,#334155 100%); }
.login-card { background:#fff; padding:40px 36px; border-radius:16px; width:360px; box-shadow:0 8px 30px rgba(0,0,0,0.2); }
.login-card h2 { text-align:center; font-size:1.1rem; margin-bottom:24px; color:#0f172a; }
.input { width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:12px; font-size:0.9rem; outline:none; }
.input:focus { border-color:#2563eb; }
.btn-auth { width:100%; padding:12px; border:none; border-radius:8px; background:#2563eb; color:#fff; font-weight:600; cursor:pointer; font-size:0.9rem; }
.btn-auth:hover { background:#1d4ed8; }

/* Layout */
.main-layout { display:flex; min-height:100vh; }

/* Sidebar */
.sidebar { width:260px; background:#fff; border-right:1px solid #e2e8f0; display:flex; flex-direction:column; flex-shrink:0; }
.sidebar-head { padding:20px 18px 14px; display:flex; align-items:center; gap:8px; border-bottom:1px solid #f1f5f9; }
.tab-count { background:#e2e8f0; color:#64748b; font-size:0.7rem; padding:2px 8px; border-radius:10px; margin-left:auto; }
.empty-list { padding:30px 18px; text-align:center; color:#94a3b8; font-size:0.8rem; flex:1; }
.tab-item { display:flex; align-items:center; padding:12px 18px; border-bottom:1px solid #f8fafc; cursor:pointer; }
.tab-item:hover { background:#f8fafc; }
.tab-item-info { flex:1; min-width:0; }
.tab-item-name { font-size:0.8rem; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.tab-item-meta { font-size:0.65rem; color:#94a3b8; margin-top:2px; }
.btn-del { padding:2px 6px; border:none; background:transparent; cursor:pointer; font-size:0.8rem; opacity:0.5; }
.btn-del:hover { opacity:1; }
.sidebar-foot { padding:16px 18px; border-top:1px solid #f1f5f9; display:flex; justify-content:space-between; align-items:center; margin-top:auto; }
.user-name { font-size:0.75rem; color:#64748b; }
.btn-logout { padding:4px 10px; border:1px solid #e2e8f0; border-radius:6px; background:#fff; color:#94a3b8; cursor:pointer; font-size:0.7rem; }

/* Content */
.content { flex:1; padding:36px 40px; overflow-y:auto; max-width:800px; }
.brand { margin-bottom:28px; }
.brand h1 { font-size:1.5rem; font-weight:700; color:#0f172a; }
.brand-sub { font-size:0.8rem; color:#64748b; margin-top:4px; }

.card { background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:18px 20px; margin-bottom:14px; }
.card-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
.label { font-size:0.65rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:2px; }

.upload-row { display:flex; gap:12px; align-items:center; }
.upload-row input[type="file"] { display:none; }
.file-drop { flex:1; padding:11px 14px; border:2px dashed #cbd5e1; border-radius:8px; background:#f8fafc; font-size:0.82rem; color:#94a3b8; cursor:pointer; text-align:center; }
.file-drop:hover { border-color:#2563eb; background:#eff6ff; }
.fn { color:#1e293b; font-weight:500; }

.btn-primary { padding:10px 22px; border:none; border-radius:8px; background:#2563eb; color:#fff; font-weight:600; font-size:0.82rem; cursor:pointer; white-space:nowrap; }
.btn-primary:hover { background:#1d4ed8; }
.btn-primary:disabled { background:#94a3b8; cursor:not-allowed; }

.mode-tag { display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.68rem; font-weight:600; margin-bottom:10px; }
.mode-tag.ai { background:#dbeafe; color:#1e40af; }
.mode-tag.mock { background:#fef3c7; color:#92400e; }

.tab-card { background:#fefdf9; }
.btn-save { padding:5px 10px; border:1px solid #e8dcc8; border-radius:6px; background:#fff; color:#b8965a; cursor:pointer; font-size:0.68rem; }
.btn-save:hover { background:#faf5eb; }

.tab-view { background:#faf5eb; border:1px solid #e8dcc8; border-radius:8px; padding:16px 18px; font-family:"SF Mono","Cascadia Code","Consolas",monospace; font-size:0.85rem; line-height:2.2; color:#1a1a1a; overflow-x:auto; white-space:pre; letter-spacing:1px; }

.result-card { text-align:center; }
.rs { font-size:0.82rem; color:#475569; margin-bottom:12px; }
.btn-download { display:inline-block; padding:12px 32px; border-radius:8px; background:#0f172a; color:#fff; font-weight:600; text-decoration:none; }
.btn-download:hover { background:#1e293b; }
</style>
.gh-link { opacity:0.5; transition:opacity 0.2s; flex-shrink:0; }
.gh-link:hover { opacity:1; }
