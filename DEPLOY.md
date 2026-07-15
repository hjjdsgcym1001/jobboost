# JobBoost 部署指南

## 推送到 GitHub

### 1. 安装 Git
下载 https://git-scm.com → 安装（全部默认选项）

### 2. 创建 GitHub 仓库
1. 打开 https://github.com → 登录/注册
2. 点右上角 "+" → New repository
3. 仓库名: `jobboost`
4. 选 Public（免费）
5. 不要勾选任何初始化选项
6. 点 Create repository

### 3. 推送代码
打开 cmd（或 VS Code 终端），进入项目目录执行：

```bash
cd C:\Users\31255\Documents\Codex\2026-07-15\w\jobboost
git init
git add .
git commit -m "init: JobBoost MVP"
git branch -M main
git remote add origin https://github.com/你的用户名/jobboost.git
git push -u origin main
```

### 4. 部署到 Railway

1. 打开 https://railway.com → 用 GitHub 登录
2. 点 "New Project" → "Deploy from GitHub repo"
3. 选择 `jobboost` 仓库
4. 部署自动开始

### 5. 配置环境变量
在 Railway Dashboard 中：
- 项目页面 → Variables → New Variable
- 添加以下变量：

| 变量名 | 值 |
|--------|-----|
| `DEEPSEEK_API_KEY` | `sk-c8112d08eb454437a94b6a11bd69e609` |
| `AI_PROVIDER` | `deepseek` |
| `DEEPSEEK_MODEL` | `deepseek-chat` |

### 6. 获取域名
部署成功后，Railway 自动生成域名：
`https://jobboost.up.railway.app`

你也可以绑定自定义域名（Settings → Domains）。

## 部署后验证
- 打开 Railway 给的域名
- 测试上传简历功能
- 测试面试模拟
- 确认 DeepSeek API 正常调用

## 后续维护
- 代码修改后: `git add . && git commit -m "修改内容" && git push`
- Railway 自动重新部署
- 查看日志: Railway Dashboard → Deployments → View Logs
