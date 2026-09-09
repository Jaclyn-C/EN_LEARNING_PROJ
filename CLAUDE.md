# CLAUDE.md — EN-learning 总规则

> 本文件是所有 Agent 在本仓库工作的总规则。项目知识库在 `.claude/memory/`，协作流程在 `.claude/workflows/`，初步方案在 `docs/PLAN.md`（母文档）。

## 1. 项目介绍

**EN-learning**：把自己的英语学习资料（PDF/Word/图片）变成练习题的个人英语学习平台。

核心链路：**上传文档 → 解析出题（有答案配对，无答案 AI 自答）→ 做题（高亮/笔记）→ 自动批改 → 生词收藏 → 背单词；另有 AI 助手随时问答。**

阶段定位：**当前单用户本地自用（MVP）**，但必须预留多用户与部署能力（见 §7、§8）。功能优先级与里程碑见 `docs/PLAN.md` §3、§8。

## 2. 技术栈

- **前端 `web/`**：React 18 + Vite + TypeScript、Ant Design 5 + Tailwind CSS、pdfjs-dist（PDF 渲染/高亮）、zustand、包管理 **pnpm**
- **后端 `server/`**：Python 3.11+ + FastAPI、SQLAlchemy 2 + Alembic（迁移）、Pydantic v2、PyMuPDF / python-docx（文档解析）、SQLite（连接串可切 PostgreSQL）
- **LLM**：智谱 GLM（OpenAI 兼容协议），经 `langchain-openai` 的 `ChatOpenAI` 接入（base_url 指向智谱）；一律经 `server/app/ai/` 抽象层调用；prompt 模板在 `server/prompts/`
- **LLM 编排与观测**：LangGraph（多步流程：出题/批改/助手）+ LangSmith（调用追踪，`.env` 开关控制）。引入这两个生态是项目的**学习目标之一**，按里程碑渐进落地（见 PLAN §5.5、§8），可以为用上它们扩展新功能

## 3. 目录结构（规划，M0 落地）

```
EN-learning/
├─ CLAUDE.md  README.md  docs/(PLAN|REQ|DESIGN)
├─ web/                     # React 前端
│  └─ src/{api, components, pages, stores, hooks, utils}
├─ server/                  # FastAPI 后端
│  ├─ app/
│  │  ├─ api/               # 路由（薄）：documents/questions/practice/words/assistant
│  │  ├─ schemas/           # Pydantic 入出参
│  │  ├─ services/          # 业务逻辑
│  │  ├─ models/            # SQLAlchemy ORM
│  │  ├─ parsing/           # 文档解析（pdf/docx/image → 文本块）
│  │  ├─ ai/                # LLM 抽象层 + 出题/批改/助手   ← ai-agent 独占
│  │  ├─ core/              # 配置 / DB / 依赖（get_current_user 等）
│  │  └─ main.py
│  ├─ prompts/              # prompt 模板（版本化）          ← ai-agent 独占
│  ├─ alembic/              # 数据库迁移
│  └─ uploads/              # 上传文件（gitignore）
└─ .claude/                 # agents / memory / workflows
```

## 4. 后端开发规范

- 分层：路由（`api/`）只做参数校验与调用 service；业务逻辑在 `services/`；ORM 在 `models/`；LLM 调用只出现在 `ai/`。
- **改表必须走 Alembic**：改 `models/` → `alembic revision --autogenerate` → `alembic upgrade head` → 在变更说明中列出迁移文件。禁止手改 SQLite 文件、禁止绕过迁移直接执行 SQL 建表。
- 配置统一 `pydantic-settings` 读 `.env`；**密钥只进 `.env`**（已 gitignore），严禁硬编码、严禁提交。
- 接口出入参用 Pydantic schema 定义（自动生成 OpenAPI 文档，前后端以此对契约）。
- 新接口在前端对接前先用 `/docs`（Swagger UI）自测通过。

## 5. 前端开发规范

- 目录职责：`api/`（请求函数，**统一封装，组件内禁止裸调 fetch/axios**）、`pages/`（路由页面）、`components/`（可复用组件）、`stores/`（zustand 全局状态）、`hooks/`、`utils/`。
- UI 优先用 AntD 组件；样式优先 Tailwind 工具类；禁止引入第二个 UI 库/状态库。
- 后端地址走环境变量（Vite 的 `.env.*`），禁止硬编码 apiBase。
- PDF 渲染与高亮封装为独立组件（基于 pdfjs-dist），不散落在页面里。

## 6. LLM 使用规范

- 所有模型调用必须经 `ai/` 层：单次调用走 `ai/llm_client.py` 的 `LLMClient`（内部封装 `ChatOpenAI`），多步流程封装为 LangGraph graph（同在 `ai/`）。模型名/base_url/key 来自 `.env`，**禁止业务代码直连 HTTP、禁止在 `ai/` 之外写模型调用**。
- LangSmith 追踪由 `.env` 的 `LANGSMITH_TRACING` 开关控制（本地默认开启），trace 即调用日志，用于调试与学习。
- prompt 一律模板文件放 `server/prompts/`（变量占位，代码加载渲染），禁止内联在业务代码里。
- 结构化输出统一 JSON：调用处必须校验，解析失败重试一次，再失败降级报错。
- 成本纪律：长文档分块出题；结果落库不重复调用；批改只对主观题走 LLM。

## 7. 多用户预留（现阶段纪律）

- 所有业务表带 `user_id`；业务代码统一经 `core` 的 `get_current_user` 依赖取当前用户（单用户阶段固定返回默认用户）。
- 禁止在业务代码里散落写死 `user_id=1`。
- 文件存储走 storage 抽象（本地 `uploads/` 实现），LLM 走 LLMClient 抽象——未来换实现不改业务代码。

## 8. 部署预留（只留口子，不实施）

- 一切配置走 `.env`（地址/端口/路径/模型名），禁止硬编码。
- 服务保持无状态（不依赖本地会话粘性），为未来容器化留余地。
- 现阶段不做：Docker、域名、HTTPS、进程守护——到部署阶段另立 DESIGN。

## 9. Git 规范

- 分支：`feature/<功能名>`（个人项目也保持习惯）；接受直接在 main 上的仅限文档微调。
- 提交信息：`type(scope): 中文描述`，scope ∈ `web`（前端）/ `server`（后端非 AI）/ `ai`（LLM 与 prompt）/ `docs`（文档）。跨前后端的变更拆多个提交。
- 禁止提交：`.env`、`uploads/`、`node_modules/`、`dist/`、`__pycache__/`、`.venv/`、`*.db`、`.claude/settings.local.json`。

## 10. Agent 协作规则

- **知识优先**：接任务先读 `.claude/memory/` 对应文档与 `docs/PLAN.md`；发现文档与代码不一致时以代码为准并反馈差异。
- **不确定即问**：涉及表结构变更、LLM prompt 大改、引入新依赖，先向用户确认。
- **验证**：后端改动至少通过 `ruff check` 且应用可启动（有测试则 `pytest`）；前端改动至少 `pnpm lint` + `pnpm build` 通过；M0 脚手架建好前此条不适用，但要说明未验证。
- 结论沉淀：架构/业务事实变化时更新 `.claude/memory/` 对应文件，不新建重复文件。
- 大范围扫描/分析优先用子代理并行，主对话保持精简。

## 11. 禁止事项

1. **禁止**提交或硬编码 API key 及任何密钥（GLM key 只在 `.env`）。
2. **禁止**绕过 `LLMClient` 抽象层直连模型 HTTP；禁止在 `ai/` 之外写模型调用。
3. **禁止**绕过前端 `src/api/` 统一请求封装；禁止硬编码后端地址。
4. **禁止**跳过 Alembic 改表（含"先建表后补迁移"）。
5. **禁止**删除或绕过多用户预留（去 `user_id`、散落写死用户）。
6. **禁止**引入与现有栈重复的框架（第二个 UI 库/状态库/ORM/HTTP 客户端）。
7. 上传的原文档内容与用户数据**只允许**发送到 GLM 与 LangSmith（调用追踪）；除这两者外，**禁止**发送到任何外部服务。
8. **禁止**在 `docs/PLAN.md` 与 `memory/` 未同步的情况下做出偏离既定方案的实现。
