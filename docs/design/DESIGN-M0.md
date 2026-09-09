# DESIGN-M0 脚手架（2026-09-09）

> 范围与验收对齐 `docs/PLAN.md` §8 M0。视觉规格见 `docs/superpowers/specs/2026-09-04-morandi-theme-design.md`（唯一权威，色值逐项照抄）。
> **git 仓库初始化与首次提交不在本次自动执行范围**——完成后经用户确认再做。

## 1. 任务包与依赖顺序

| Agent | 独占目录 | 交付 | 依赖 |
|---|---|---|---|
| backend-agent | `server/`（除 `app/ai/`、`prompts/`，仅建占位） | FastAPI 骨架 + Alembic 首迁移 + 可启动可测 | 无 |
| frontend-agent | `web/` | Vite+React18+TS 骨架 + 莫兰迪主题系统 + 演示页 | 无（与 backend 并行） |
| ai-agent | `server/app/ai/`、`server/prompts/` | LLMClient（ChatOpenAI 直连 GLM）+ prompt 模板机制 + 真实调用冒烟脚本 | **backend 完成后** |

## 2. 关键技术决定

1. **`.env` 唯一位置：项目根**（已存在）。`Settings.env_file` 用绝对路径指向根 `.env`（相对 `core/config.py` 解析）；同时用 `python-dotenv` 把根 `.env` 载入 `os.environ`（LangSmith SDK 只认进程环境变量），不覆盖已有变量。
2. **数据库**：SQLite，`DATABASE_URL=sqlite:///./enlearning.db` 相对 CWD（约定从 `server/` 起服务）；Alembic 首迁移只建 `users` 表（get_current_user 的默认用户依赖它）；其余表 M1 走正常 DESIGN 流程。
3. **LLM 依赖归 ai-agent**：`langchain-openai` 由 ai-agent 加入 requirements 并安装；backend 骨架不含 LLM 依赖，但 `Settings` 预留全部 LLM/LangSmith 字段。
4. **前端**：React 锁 18（非 19，按 CLAUDE.md 定稿）；Tailwind 用 v4（`@theme` 把语义色映射到 `--enl-*` CSS 变量，等价实现设计稿的"tailwind.config 引用变量"意图）；不装路由（M0 单演示页）；HTTP 客户端用 axios（经 `src/api/` 统一封装）；`VITE_API_BASE` 走 `.env.development`；后端 CORS 放行 `localhost:5173`。
5. **pnpm 未预装**：frontend-agent 先 `corepack enable && corepack prepare pnpm@10 --activate`（失败则 `npm i -g pnpm`）。

## 3. 验收标准（汇总）

- 后端：`ruff check` 通过；`uvicorn app.main:app`（server/ 下）启动且 `/api/health` 200（顺带验证 DB）；`pytest` 通过；`alembic current` 在 head。
- 前端：`pnpm lint` + `pnpm build` 通过；演示页三主题即时切换、刷新保持、非法值回落 iris、错误态无高饱和红（用户肉眼验收）。
- AI 层：代码过 ruff；冒烟脚本可运行——`.env` 有真实 key 则完成一次真实 GLM 调用并打印 token 用量，key 未填则跳过真实调用并打印清晰指引（退出码非 0）。

## 4. 风险与备注

- GLM key / LangSmith key 用户尚未填：不影响 1、2 两包验收；真实调用与 trace 验证待用户填 key 后补跑。
- Tailwind v4 与设计稿（v3 写法）差异已在上文 §2.4 说明，属实现方式等效，非契约变更。
- LangSmith 验证方式：填 key 后设 `LANGSMITH_TRACING=true`，smith.langchain.com 的 `en-learning` 项目应出现冒烟调用 trace。
