# GuitarTab AI - 电吉他 AI 扒谱工具

> 上传音频文件，AI 自动分析音高，生成吉他六线谱

## ✨ 功能

- 🎵 **音频上传** — 支持 WAV / MP3 / OGG / FLAC / M4A 格式
- 🧠 **AI 音高检测** — 基于 Google basic-pitch（TensorFlow）自动提取 MIDI 音符
- 🎸 **六线谱生成** — MIDI 音符自动映射到标准定弦吉他的弦号与品位
- 👁️ **可视化** — SVG 指板图 + ASCII 六线谱文本 + 数据表格三种展示

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | Python FastAPI + uvicorn |
| AI | basic-pitch (TensorFlow) + librosa |
| 可视化 | SVG（内联组件） |

## 📦 项目结构

```
guitar-tab-ai/
├── backend/
│   ├── main.py              # FastAPI 服务入口（CORS + 文件上传）
│   ├── tab_converter.py     # 核心算法：MIDI → 弦号/品位映射
│   ├── requirements.txt     # Python 依赖清单
│   └── python-packages/     # 离线打包依赖（自包含部署）
└── frontend/
    ├── src/
    │   ├── App.vue           # 根组件：上传 + 结果展示
    │   ├── main.ts           # Vue 应用启动入口
    │   └── components/
    │       └── FretBoard.vue # SVG 指板可视化组件
    ├── index.html
    ├── package.json
    └── vite.config.ts        # 开发服务器 + API 代理
```

## 🚀 快速开始

### 1. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

后端默认运行在 http://localhost:8000

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 http://localhost:5173

> 前端 `/api/*` 请求通过 Vite proxy 自动转发到后端 8000 端口。

### 3. 使用

1. 浏览器打开 http://localhost:5173
2. 选择音频文件（或使用测试模式自动生成示例数据）
3. 查看 AI 生成的六线谱 + 指板可视化

## 🔬 核心算法

**MIDI → 六线谱转换**（`tab_converter.py`）：

1. 标准吉他定弦为 EADGBE（MIDI 40/45/50/55/59/64）
2. 对每个音符，遍历 6 根弦计算品位 = 音高 − 空弦音高
3. 选择品位最低的合法位置（低把位优先，更符合演奏习惯）
4. 落在 0-19 品范围内即为有效

## 📡 API

### `GET /`
健康检查，返回 AI 模式是否可用。

### `POST /api/upload`
上传音频文件，返回六线谱分析结果。

**请求**：`multipart/form-data`，字段名 `file`

**响应**：
```json
{
  "filename": "riff.wav",
  "size_bytes": 123456,
  "mode": "ai",
  "notes": [
    {
      "pitch": 64,
      "string": 1,
      "fret": 0,
      "start_time": 0.5,
      "end_time": 1.0
    }
  ],
  "tab_text": "1(e) |  0 -- --\n2(B) | --  0 --\n..."
}
```

## 🧪 开发模式

- 当 `basic-pitch` / `librosa` 未安装时，后端自动降级为 **模拟模式**
- 模拟模式返回预设的示例音符（E 小调五声音阶动机）
- 前端同样正常渲染，方便无 AI 环境下调试 UI

## 📝 待扩展

- [ ] 多音轨支持（和弦 / 双音同时检测）
- [ ] 节奏量化（八分/十六分音符精度）
- [ ] 导出 GP5/Guitar Pro 格式
- [ ] 用户上传历史记录
- [ ] Docker 一键部署

## 📄 许可

MIT License
