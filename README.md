# JobBoost - AI Resume Optimizer & Interview Assistant

用 AI 让你的简历更出色。上传简历，智能分析和优化；AI 面试模拟，提升面试技能。

## 快速开始

### 1. 安装依赖

```bash
cd jobboost
pip install -r backend/requirements.txt
```

### 2. 配置 API Key（可选）

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入你的 API Key：
- OpenAI: `OPENAI_API_KEY=sk-xxx`
- Anthropic: `ANTHROPIC_API_KEY=sk-ant-xxx`

> **无需 API Key 也能运行**：Demo 模式会返回示例数据，方便你快速体验和演示。

### 3. 启动服务

```bash
python run.py
```

打开 http://localhost:8000 即可使用。

## 功能

- **简历上传与解析** — 支持 PDF / DOCX 格式
- **AI 简历优化** — 智能分析内容，提供优化建议
- **ATS 匹配检测** — 评估简历通过筛选的概率
- **面试模拟** — 基于简历定制面试题，AI 评估回答
- **JD 定制优化** — 粘贴职位描述获取精准建议

## 技术栈

- 后端：Python FastAPI
- AI：OpenAI GPT / Anthropic Claude
- 前端：HTML + Tailwind CSS + Vanilla JS
- 文件处理：PyMuPDF + python-docx

## 项目结构

```
jobboost/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── resume_parser.py      # 简历解析模块
│   ├── ai_service.py         # AI 服务封装
│   ├── models.py             # 数据模型
│   ├── requirements.txt      # Python 依赖
│   └── .env.example          # 环境变量模板
├── frontend/
│   ├── templates/            # HTML 模板
│   │   ├── base.html         # 基础模板
│   │   ├── index.html        # 首页 + 上传
│   │   ├── result.html       # 分析结果页
│   │   ├── interview.html    # 面试模拟页
│   │   └── pricing.html      # 定价页
│   └── static/
│       ├── css/style.css     # 样式
│       └── js/main.js        # 前端逻辑
├── run.py                    # 启动入口
└── README.md
```

## 部署

### Vercel（推荐）

1. 将项目推送到 GitHub
2. 在 Vercel 中选择 `Import` → 选择 `jobboost` 仓库
3. Framework 选择 `Other`
4. Build Command 留空
5. Output Directory 留空
6. 添加环境变量（API Keys）
7. 部署完成

### Railway

```bash
railway login
railway up
```

## 商业模式

| 套餐 | 价格 | 核心功能 |
|------|------|----------|
| Free | $0 | 1 次简历分析 |
| Pro | $19/月 | 无限分析 + 面试模拟 |
| Pro+ | $39/月 | 全部功能 + 优先支持 |

## License

MIT
