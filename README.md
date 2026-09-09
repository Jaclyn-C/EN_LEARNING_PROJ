# EN-learning

把自己的英语学习资料（PDF / Word / 图片）变成练习题的个人英语学习平台：AI 出题与批改、做题高亮笔记、生词本与背单词、AI 学习助手。

- 📄 产品初步方案：[docs/PLAN.md](docs/PLAN.md)（功能清单 / 技术选型 / 数据模型 / 里程碑 / 待确认问题）
- 📋 Agent 总规则：[CLAUDE.md](CLAUDE.md)
- 🤖 Agent 团队：`.claude/agents/`（6 个角色）｜流程：`.claude/workflows/development-flow.md`｜知识库：`.claude/memory/`

## 当前状态

**方案阶段**——方案与 Agent 团队已就绪，代码尚未开始（从 M0 脚手架起步，见 PLAN §8）。

## 技术栈

React 18 + Vite + TypeScript + AntD 5 + Tailwind（前端）｜FastAPI + SQLAlchemy + Alembic + SQLite（后端）｜智谱 GLM（LLM，经抽象层接入）

## 如何使用 Agent 团队开发这个项目

### 前提（各做一次）

1. **用 Claude Code 打开本文件夹作为工作区根目录**（`EN-learning/` 必须是打开的根，`.claude/agents/` 才会被加载；嵌在别的目录下打开则 agent 不生效）。
2. 首次开发前初始化 git：`git init`（保持 feature 分支习惯，见 CLAUDE.md §9）。
3. 创建密钥配置：`cp .env.example .env`，填入你的智谱 API key。`.env` 已被 gitignore，**不会也不允许提交**。

### 日常用法

直接用自然语言提需求，主对话会按各 agent 的 description 自动委派；也可以点名：

```
「让 architect-agent 出 M0 脚手架的技术方案」          ← 开始写代码前先做这个
「用 product-agent 梳理一下背单词模块的需求」
「backend-agent 和 frontend-agent 按这份 DESIGN 分头实现」
「reviewer-agent 评审一下这次改动」
「这个批改效果不好，让 ai-agent 调一下批改的 prompt」
```

### 开发流程

```
想法 → (product-agent 出 REQ，小需求可跳过)
     → architect-agent 出 DESIGN（含 backend/frontend/ai 任务包）
     → 建 feature 分支 → backend ∥ frontend ∥ ai 并行实现（目录互斥）
     → reviewer-agent 评审 → 修复 → 提交
```

详见 `.claude/workflows/development-flow.md`。

### 角色速查

| Agent | 职责 | 可写范围 |
|---|---|---|
| product-agent | 需求梳理 → REQ 文档 | `docs/requirements/` |
| architect-agent | 技术方案与任务包 → DESIGN | `docs/design/` |
| backend-agent | FastAPI 接口/业务/解析/迁移 | `server/`（除 `ai/`、`prompts/`） |
| frontend-agent | React 页面与交互 | `web/` |
| ai-agent | GLM 抽象层、prompt、出题/批改/助手 | `server/app/ai/`、`server/prompts/` |
| reviewer-agent | 只读评审、分级报告 | 无（只读） |

## 本地运行（M0 之后补充实际命令）

```bash
# 后端
cd server && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd web && pnpm install && pnpm dev
```
# EN_LEARNING_PROJ
