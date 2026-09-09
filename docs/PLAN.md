# EN-learning 初步方案（v0.1）

> 状态：**初稿**。本文档是后续需求文档（`docs/requirements/REQ-*.md`）与技术设计（`docs/design/DESIGN-*.md`）的母文档。
> 待确认问题见 §9，确认后更新版本号。

## 1. 项目定位

一句话：**把自己的英语学习资料变成练习题的个人英语学习平台。**

三条核心链路：

1. **资料 → 题目**：上传文档（PDF / Word / 图片）→ 解析出文本与答案 → AI 出题（资料自带答案则配对，没有则 AI 自己作答）→ 在线做题（高亮、笔记）→ 自动批改
2. **生词 → 背诵**：做题/阅读中收藏生词，也可批量导入自己的单词 → 多种模式背单词（如看中文打字拼英文）
3. **AI 助手**：随时提问——词义、句意、语法、这句话怎么写

**阶段定位**：当前为单用户本地自用（MVP）；表结构与业务代码预留多用户能力（§5.3）；产品成熟后再考虑部署（§5.4 仅预留，不实施）。

## 2. 核心使用流程（用户故事）

| # | 用户故事 | 所属功能域 |
|---|---|---|
| U1 | 我把一份真题 PDF 传上来，系统生成一套练习题（答案在文档末尾，自动配对） | 文档与出题 |
| U2 | 我传一份纯阅读材料（无答案），AI 也能出题并给出参考答案与解析 | 文档与出题 |
| U3 | 做题时我可以高亮题干关键词、写笔记；交卷后客观题直接判分，简答题 AI 批改给评语 | 做题与批改 |
| U4 | 遇到不认识的词一键加入生词本；我还能把别处攒的单词批量导进来，用"看中文拼英文"等模式背 | 生词与背单词 |
| U5 | 我选中一句话问 AI：这句话什么意思 / 这个语法为什么这样用 / 帮我换个写法 | AI 助手 |

## 3. 功能清单与优先级

### P0 — MVP（核心闭环，先跑通"上传→做题→批改"）

| 功能 | 说明 |
|---|---|
| 文档上传 | 支持 pdf / docx / txt / 常见图片格式（jpg/png）；大小与格式校验 |
| 文档解析 | PDF 文本层直接抽取（PyMuPDF）；Word 用 python-docx；图片走视觉模型 OCR；输出纯文本 + 页码/位置信息 |
| 答案识别 | 若文档含答案区（如"Answer Key"），解析出答案并与题目配对；识别不到则标记"无答案" |
| AI 出题 | 按文本分块生成题目；题型：单选、填空、判断（简答进 P1）；每题带答案、解析、来源定位 |
| 无答案自答 | 无标准答案时由 LLM 生成参考答案，标记来源为 AI |
| 做题页 | 按题集顺序作答；**题干高亮**（划词/涂色）；**笔记**（挂在题目上） |
| 自动批改 | 客观题规则判分；简答题 LLM 批改（有标准答案按标准评，无则按参考答案评），输出对错/分数/评语 |
| 生词收藏 | 做题页/文档中划词收藏进生词本 |

### P1 — 单词模块 + AI 助手

| 功能 | 说明 |
|---|---|
| 单词导入 | 批量粘贴（每行 `word 释义`）或导入 txt/csv；查重合并 |
| 背单词 | 多种模式，优先实现：**看中文打字拼写英文**（拼写比对、错字母提示）、看英文选中文；错词自动进重练队列 |
| 简答题型 | 出题支持简答/翻译/作文（批改链路复用） |
| AI 助手 | 对话式问答；支持以"当前题目/选中句子"为上下文提问（词义/句意/语法/改写/写作指导） |

### P2 — 打磨与扩展

错题本（按错因归类）、学习统计与复习计划（SM-2 间隔重复）、听力（TTS 发音）、文档高亮笔记（在原文 PDF 上，而不仅题目）、多用户账号体系、正式部署、移动端适配。

## 4. 技术选型

| 层 | 选型 | 理由 | 未来演进 |
|---|---|---|---|
| 前端 | **React 18 + Vite + TypeScript** | 用户指定 React；Vite 启动快、TS 保证中型项目可维护 | 不变 |
| UI | Ant Design 5 + Tailwind CSS | AntD 表单/表格/上传等组件齐全，适合工具型产品；Tailwind 快速调样式 | 不变 |
| PDF | pdfjs-dist | PDF 渲染 + 文本层选取，做高亮的事实标准 | 不变 |
| 状态 | zustand | 轻量，够用；不引入大型数据层 | 可加 React Query |
| 后端 | **Python 3.11+ + FastAPI** | 文档解析生态最强（PyMuPDF/python-docx）；GLM 官方 SDK 与 AI 生态以 Python 为主；自带 OpenAPI 文档便于前后端对契约 | 不变 |
| ORM/迁移 | SQLAlchemy 2 + Alembic | 迁移工具链成熟，改表有版本历史 | 不变 |
| 数据库 | **SQLite 起步** | 单用户本地零运维 | 连接串切换 PostgreSQL（代码不动） |
| 文件存储 | 本地 `server/uploads/`（storage 抽象接口） | 自用最简单 | 换 OSS/S3 只换实现类 |
| LLM | **智谱 GLM**（已有 API key），OpenAI 兼容协议接入 | 用户已购 token；出题/批改/对话均可用；图片 OCR 用其视觉模型 | 经 LLM 抽象层，可换任意 OpenAI 兼容模型 |
| LLM 编排 | **LangChain 生态**：langchain-openai（ChatOpenAI 直连 GLM）+ LangGraph（多步流程）+ LangSmith（追踪） | **学习这三者是项目目标之一**；LangGraph 适合出题/批改等多步流程与后续 agent；LangSmith 免费 5k traces/月够个人用 | 各组件按里程碑渐进引入（§8），业务代码只依赖 `ai/` 门面 |
| 包管理 | 前端 pnpm / 后端 venv + pip | — | — |

> GLM 具体型号（文本/视觉）在 M0 用真实题目做一次小样本对比后定，写进 `.env` 配置，代码不感知型号。

## 5. 系统架构

### 5.1 模块划分

```
EN-learning/
├─ web/                        # React 前端（Vite + TS）
│  └─ src/{api, components, pages, stores, hooks, utils}
├─ server/                     # FastAPI 后端
│  ├─ app/
│  │  ├─ api/                  # 路由层（薄）：documents/questions/practice/words/assistant
│  │  ├─ schemas/              # Pydantic 入出参
│  │  ├─ services/             # 业务逻辑
│  │  ├─ models/               # SQLAlchemy ORM
│  │  ├─ parsing/              # 文档解析流水线（pdf/docx/image→文本）
│  │  ├─ ai/                   # LLM 抽象层 + 出题/批改/助手调用   ← ai-agent 主场
│  │  ├─ core/                 # 配置(pydantic-settings)/DB/依赖(如 get_current_user)
│  │  └─ main.py
│  ├─ prompts/                 # prompt 模板文件（版本化）          ← ai-agent 主场
│  ├─ alembic/                 # 数据库迁移
│  └─ uploads/                 # 上传文件（gitignore）
├─ docs/                       # PLAN / REQ / DESIGN
└─ .claude/                    # Agent 团队
```

### 5.2 核心数据流（出题闭环）

```
上传文件 → storage 存档 → parsing 解析出 文本块(+页码)
        → 有答案区：解析答案 → 与题目配对
        → ai/ 出题（分块→prompt→结构化 JSON→校验落库）
做题页答题 → 客观题规则判分 / 主观题 ai/ 批改（JSON：分数+评语）
        → 错词划词收藏 → 生词本
```

### 5.3 多用户预留（现在就做，成本极低）

1. **所有业务表带 `user_id`** 外键；
2. 业务代码统一通过 `core` 的 `get_current_user` 依赖取当前用户——单用户阶段它固定返回默认用户（id=1），未来加认证只改这一处；
3. 禁止业务代码散落写死 `user_id=1`；
4. 文件与 LLM 调用都过抽象接口（storage / LLMClient）。

**现在不做**：注册登录、权限、数据隔离测试——等产品成熟上多用户时再补。

### 5.4 部署预留（只留口子，不实施）

配置全部走 `.env`（不硬编码地址/端口/路径）；服务保持无状态（文件路径、DB 均配置化）；Docker 化与域名/HTTPS 等到部署阶段再说。

### 5.5 LLM 抽象层（LangChain 生态，2026-09-09 定稿）

- `server/app/ai/llm_client.py` 提供 `LLMClient`：`chat(messages, json_schema=None, vision=False)`，内部封装 `langchain-openai` 的 `ChatOpenAI`（base_url 指向智谱）。模型名、base_url、key 全部来自 `.env`。
- 多步流程（出题管线、批改分流、AI 助手）封装为 **LangGraph** graph，代码同在 `ai/`；业务代码不感知 graph 内部结构。
- **LangSmith** 追踪：`.env` 设 `LANGSMITH_TRACING=true` 自动记录全部调用，trace 即调试日志；本地默认开启，可随时关闭不影响功能。
- 不变量：所有业务只依赖 `ai/` 门面——换模型、换供应商、换编排实现不改业务代码。引入顺序：M0 ChatOpenAI+LangSmith → M1 出题 graph → M2 批改路由 → M4 助手 agent。

## 6. 数据模型草案

| 表 | 用途 | 关键字段 |
|---|---|---|
| users | 用户（预留） | id, name, email, created_at |
| documents | 上传的文档 | id, **user_id**, title, file_type, file_path, status(uploaded/parsed/failed), raw_text?, created_at |
| document_chunks | 解析后的文本块（出题单元） | id, document_id, seq, text, page_no |
| question_sets | 题集（一份练习） | id, **user_id**, document_id?, name, status, created_at |
| questions | 题目 | id, question_set_id, type(choice/blank/judge/short), stem, options(json), answer, analysis, answer_source(doc/ai), source_chunk_id, difficulty |
| attempts | 答题与批改记录 | id, **user_id**, question_set_id, question_id, answer, is_correct?, score?, ai_feedback?, submitted_at |
| highlights | 高亮 | id, **user_id**, target_type(question/document), target_id, text, position(json), color |
| notes | 笔记 | id, **user_id**, target_type, target_id, content, created_at |
| words | 生词本 | id, **user_id**, word, meaning?, example?, source(question/document/manual), familiarity, created_at |
| word_reviews | 背单词记录 | id, **user_id**, word_id, mode, is_correct, reviewed_at（P2 加 SM-2 字段） |
| chat_sessions / chat_messages | AI 助手会话 | id, **user_id**, role, content, context_ref?(关联题目/句子) |

> 粗体 `user_id` = 多用户预留字段。表结构以第一个 DESIGN 定稿为准，之后一切变更走 Alembic。

## 7. LLM 应用设计

| 场景 | 输入 | 输出（结构化 JSON） | 模型 |
|---|---|---|---|
| 图片 OCR | 图片 | 文本 + 置信度标记 | 视觉模型 |
| 题目/答案识别与配对 | 文档全文分块 | 题目列表 + 答案映射 | 文本模型 |
| 出题（无答案） | 文本块 + 题型要求 | [{type, stem, options, answer, analysis, 难度}] | 文本模型 |
| 主观题批改 | 题目 + 参考答案 + 学生答案 | {score, is_correct, 评语, 错误点} | 文本模型 |
| AI 助手 | 对话历史 + 可选上下文（选中句/题目） | 自然语言（流式） | 文本模型 |

工程纪律（写入 CLAUDE.md，由 ai-agent 执行）：

- prompt 一律模板文件放 `server/prompts/`，不内联在代码里；
- 结构化输出统一 JSON，调用处必须校验，解析失败重试一次后降级报错；
- 长文档分块出题（按 token 上限切块，保留页码回溯），结果落库不重复调用；
- 批改只对主观题走 LLM；每次真实调用的 token 消耗记录在测试脚本输出里；
- 所有调用经 `ai/` 门面（LLMClient / LangGraph graph），LangSmith trace 作为调用记录与调试入口。

## 8. 里程碑

| 里程碑 | 内容 | 验收标准 |
|---|---|---|
| **M0 脚手架** | web/server 工程初始化、LLM 抽象层连通 GLM（ChatOpenAI）、LangSmith 追踪打通、.env 体系、git 仓库 | 前后端本地能启动；一次真实 GLM 调用返回且能在 LangSmith 看到 trace；做一次文本/视觉模型小样本选型 |
| **M1 出题闭环（后端）** | 上传→解析→分块→出题→落库，含答案配对与无答案自答 | 传一份真题 PDF 和一份纯阅读材料，均能产出带答案解析的题目 JSON |
| **M2 做题体验** | 做题页（高亮/笔记）、自动批改、成绩页 | 完整走一遍 U1-U3；批改结果可读可用 |
| **M3 单词模块** | 生词收藏、批量导入、看中文拼英文模式、错词重练 | 走通 U4 |
| **M4 AI 助手** | 对话页 + 选中内容上下文提问 | 走通 U5 |
| **M5 打磨** | 错题本、统计、（远期）多用户与部署 | 按届时需求定 |

## 9. 待确认问题

1. **高亮对象**：只高亮题目文本，还是也要在原文 PDF 上高亮？（后者 M2 成本明显增加，建议 P0 只做题干高亮，原文高亮进 P2）
2. **出题默认参数**：题型组合与数量（建议默认：单选+填空+判断，每文本块 2-3 题，可调）？
3. **主观题评分制**：百分制分数还是等级（Good/Fair/Poor）？（建议等级制起步）
4. **图片的主要来源**：拍照的纸质资料还是 App 截图？（影响 OCR 预处理策略）
5. **单词导入格式**：粘贴文本（每行 `word 释义`）够不够，还是要支持 Excel/csv？
6. **背单词模式优先级**：建议"看中文拼英文（打字）"最先做，其余（选义、听写、例句填空）按反馈排。

## 10. 下一步

用本仓库的 Agent 团队推进（见 `.claude/workflows/development-flow.md`）：

1. 确认 §9 问题 → 更新本文档；
2. 第一件事：让 **architect-agent** 产出 M0 脚手架的 DESIGN（含前后端初始化方案与任务包）；
3. 之后按里程碑逐个走 需求 → 设计 → 开发 → 评审 流程。
