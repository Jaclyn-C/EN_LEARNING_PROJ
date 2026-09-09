# architecture — 技术架构与决策

> 状态：方案阶段（代码未开始）。M0 落地后由 architect/backend/frontend agent 持续更新。

## 技术栈定稿（2026-09-04，用户确认）

| 决策 | 选择 | 理由/备注 |
|---|---|---|
| 前端 | React 18 + Vite + TypeScript | 用户指定 React |
| UI | Ant Design 5 + Tailwind CSS | 工具型产品组件齐全 |
| PDF | pdfjs-dist | 渲染 + 文本层高亮 |
| 状态 | zustand | 轻量；禁止第二状态库 |
| 后端 | Python 3.11+ + FastAPI | 文档解析与 GLM 生态最顺；自带 OpenAPI |
| ORM | SQLAlchemy 2 + Alembic | 改表必走迁移 |
| 数据库 | SQLite 起步 | 连接串切 PostgreSQL 不改代码 |
| LLM | 智谱 GLM（用户已有 key），OpenAI 兼容协议 | 具体型号 M0 实测后定，配置化 |
| LLM 编排 | LangChain 生态（langchain-openai / LangGraph / LangSmith） | 2026-09-09 用户定稿：**学习这三者是项目目标之一**，渐进引入，业务只依赖 ai/ 门面 |
| 包管理 | pnpm / venv+pip | — |

## 前端视觉与主题（2026-09-04 定稿，用户逐项确认）

- **莫兰迪紫三主题可切换，默认 iris（鸢尾蓝紫 #7D7FA8）**；另两套：mist 雾紫奶油 #9F8BB8、mauve 藕紫奶茶 #AC8DA5
- 形状语言：奶油圆润——卡片 18px、控件 12px、CTA 胶囊、带主色调软阴影、135° 淡渐变页面底、系统圆润字体栈
- 架构：TS 色板双轨注入（palettes.ts 单一事实来源 → AntD ConfigProvider token + 根节点 CSS 变量，Tailwind 引用变量）；zustand persist 切换；仅浅色，CSS 变量语义命名预留深色
- 关键取舍：**错误态用灰粉/灰杏/灰玫，禁止高饱和红**（保莫兰迪感）
- 详见 `docs/superpowers/specs/2026-09-04-morandi-theme-design.md`；随 M0 前端脚手架落地，含演示页验收

## 产品阶段决策

- 当前单用户本地自用；**多用户前置**：业务表全带 user_id + get_current_user 依赖（现固定返回默认用户）+ storage/LLM 抽象
- 部署只留口子（全配置走 .env、服务无状态），不做 Docker/域名
- 前后端同仓 monorepo：`web/` + `server/`

## 目录规划

见 `CLAUDE.md` §3（权威版本）。关键归属：`server/app/ai/` + `server/prompts/` 归 ai-agent，其余 server 归 backend-agent，`web/` 归 frontend-agent。

## LLM 抽象层设计（PLAN §5.5，2026-09-09 更新为 LangChain 生态）

- `server/app/ai/llm_client.py` → `LLMClient.chat(messages, json_schema=None, vision=False)`，内部封装 langchain-openai 的 `ChatOpenAI`（base_url 指向智谱）
- 多步流程（出题/批改/助手）封装为 LangGraph graph，同在 `ai/`，业务代码不感知
- 模型名/base_url/key 全部来自 `.env`（ZHIPU_API_KEY / LLM_BASE_URL / LLM_MODEL / LLM_VISION_MODEL）
- LangSmith 追踪：`.env` 的 LANGSMITH_TRACING 开关，本地默认开，trace 即调用日志
- 结构化输出统一 JSON + 调用处校验 + 失败重试一次 + 降级报错
- prompt 模板文件化于 `server/prompts/`，禁止内联业务代码
- 引入节奏：M0 ChatOpenAI+LangSmith → M1 出题 graph → M2 批改路由 → M4 助手 agent；写作评分功能后续用 LangSmith 评估（datasets/evals）
- 隐私规则（CLAUDE.md §11.7）已放宽：数据允许发 GLM + LangSmith，其余外部服务仍禁止

### M0 落地事实（2026-09-09，ai-agent）

- `LLMClient` 已实现并实测连通（真实 key）：普通对话 + 结构化输出均一次通过；`last_usage`/`last_attempts` 供 token 记账；`get_llm_client()` lru_cache 单例
- 结构化输出方案（实测智谱兼容）：`response_format={"type":"json_object"}` + JSON Schema 注入 system + 本地校验（Pydantic 类或轻量 JSON Schema 子集校验）+ 失败回灌校验错误重试一次 → `LLMError`。不用 `with_structured_output()`（GLM 各型号 function calling 遵从度不一，且封装无法回灌重试）
- prompt 机制：`app/ai/prompt_loader.py::load_prompt(name, **vars)`，str.format 占位；模板内**字面大括号必须写 `{{` `}}`**（JSON 示例常见坑）
- 依赖：langchain-openai==1.6.1、langsmith==0.12.2（连带 openai 3.10 / langchain-core 1.6.2）
- LangSmith 机制：环境变量驱动（LANGSMITH_TRACING 需在 langchain 首次求值前进 os.environ；`app.core.config` 导入时 load_dotenv 已保证）。当前 .env：TRACING=false、API_KEY 未填
- 文本模型小样本选型（scripts/compare_models.py，2026-09-09）：glm-4-plus / glm-4-air / glm-4-flash 结构化输出全部零重试通过；质量粗评 plus 11/11×2、air 9/11 与 11/11（解析偶发过短）、flash 11/11×2；耗时 plus 4.6-8.9s、air 4.6-5.3s、flash 10.9-16.2s；token 每次约 0.8k in / 0.3k out。报告：`server/scripts/out/model_compare_2026-09-09.md`。当前 .env 默认模型 glm-5.2（冒烟通过）；最终型号待用户定
- 冒烟脚本：`scripts/test_llm.py`（key 为占位符时打印指引并以非 0 退出，不发调用）

## 已定工程纪律（详见 CLAUDE.md）

改表必走 Alembic；密钥只进 .env；前端请求统一 src/api/ 封装；上传文件存 `server/uploads/`（gitignore）。

## 待 M0 确认的技术点

- GLM 文本/视觉具体型号（小样本实测：出题质量、JSON 遵从度、token 成本）
- 文本分块的具体 token 上限与切分策略
