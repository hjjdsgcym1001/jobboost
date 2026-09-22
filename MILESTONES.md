# 1.4 Milestone 划分

> 说明：当前提交包是 ZIP 快照，不包含 `.git` 历史，因此本文件**不虚构 SHA**。在原始 Git 仓库中运行 `python scripts/repo_quality_check.py` 会读取真实历史，并在可可靠匹配时填入 Commit 起止 SHA。

| Milestone | 开发顺序 | 独立目标 | 主要代码范围 | 可验证信号 |
|---|---:|---|---|---|
| M1 Core resume ingestion | 1 | 完成 PDF/DOCX 上传、解析和结构化结果 | `backend/main.py`, `resume_parser.py`, `models.py` | `/api/resume/upload`, `parse_resume` |
| M2 AI resume optimization | 2 | 完成 AI 简历分析、ATS、关键词缺口和模板化 | `backend/main.py`, `ai_service.py`, `models.py` | `/api/resume/analyze`, `analyze_resume`, `TEMPLATE_PROMPTS` |
| M3 Interview assistant | 3 | 完成面试题生成、回答反馈和会话状态 | `backend/main.py`, `ai_service.py`, `models.py` | `/api/interview/start`, `/answer` |
| M4 Monetization & deployment | 4 | 完成套餐/学生验证/支付与部署入口 | `backend/payment.py`, `run.py`, `Dockerfile`, `railway.json`, `koyeb.yaml` | `/api/payment`, `ALIPAY`, `PORT` |

## Commit 区间选择规则

1. 只在 Git 历史可用时选择区间。
2. 按 `git log --reverse` 的开发时间顺序处理。
3. 以与 Milestone 目标高度相关的 commit subject 作为锚点。
4. 起止 Commit 必须形成连续区间；不跨越无关分支。
5. 如果无法可靠从 commit message 判断归属，则标记 `not-inferred`，不猜测。

这样可以避免为了满足评分而人为制造或虚构 Commit 区间。
