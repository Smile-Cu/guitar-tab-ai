# GuitarTab AI — AI 智能扒谱平台

> 上传音频，AI 自动识别音符，生成六线谱并导出 MIDI 文件。支持用户系统与吉他谱管理。

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🎵 AI 扒谱 | 基于 Google basic-pitch (ONNX) 自动提取音高 |
| 🎸 六线谱 | 多行分块 ASCII 六线谱，Guitar Pro 风格渲染 |
| 💾 谱库管理 | 用户登录、保存/删除/查看吉他谱 |
| 📥 MIDI 导出 | 标准 MIDI 文件，Guitar Pro / MuseScore 可直接打开 |
| 🔐 用户系统 | JWT 认证，SQLite 数据库 |

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | Python FastAPI + uvicorn |
| AI | basic-pitch (TensorFlow/ONNX) + librosa |
| 数据库 | SQLite (可切换 MySQL) |
| 认证 | JWT (HMAC-SHA256) |
| MIDI | pretty_midi |

## 📁 项目结构

```
guitar-tab-ai/
├── backend/
│   ├── main.py              # FastAPI 入口 (路由/认证/上传)
│   ├── tab_converter.py     # 核心算法 (音高→六线谱→MIDI)
│   ├── database.py          # SQLite 数据库 + JWT 认证
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.vue          # 根组件 (登录/上传/谱库)
    │   └── main.ts          # Vue 入口
    ├── index.html
    ├── package.json
    └── vite.config.ts
```

## 🚀 快速开始

### 1. 启动后端 (Python 3.12)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 使用

1. 打开 http://localhost:5173
2. 注册/登录账号
3. 上传吉他音频 (wav/mp3/ogg/flac/m4a)
4. 查看 AI 生成的六线谱
5. 保存到谱库或下载 MIDI 文件

## 📡 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/register | 注册 |
| POST | /api/login | 登录 |
| POST | /api/upload | 上传音频 |
| GET | /api/download/{name} | 下载 MIDI |
| GET | /api/tabs | 谱库列表 |
| GET | /api/tabs/{id} | 获取曲谱 |
| POST | /api/tabs | 保存曲谱 |
| DELETE | /api/tabs/{id} | 删除曲谱 |

## 📄 许可

MIT License
