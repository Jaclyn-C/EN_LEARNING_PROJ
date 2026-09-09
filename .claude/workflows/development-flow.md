# 开发工作流（development-flow）

> 总规则见 `CLAUDE.md`；Agent 定义见 `.claude/agents/`；产品方案见 `docs/PLAN.md`。

```
想法/需求 → (product-agent 出 REQ，小需求可跳过)
         → architect-agent 出 DESIGN（含 backend/frontend/ai 任务包）
         → 建 feature 分支 → backend ∥ frontend ∥ ai 并行实现 → reviewer-agent 评审 → 修复 → 提交
```

## 任务包目录边界（并行不冲突）

| Agent | 独占目录 |
|---|---|
| backend-agent | `server/app/{api,core,models,schemas,services,parsing}/**`、`server/alembic/**`、`server/tests/**`、server 根配置 |
| frontend-agent | `web/**` |
| ai-agent | `server/app/ai/**`、`server/prompts/**` |
| product / architect | `docs/**`（各自子目录） |
| reviewer-agent | 无（只读） |

---

## 步骤 1：需求（可选，复杂需求才走）

| 项 | 说明 |
|---|---|
| 责任 | product-agent |
| 输出 | `docs/requirements/REQ-*.md`：功能描述、交互、验收标准、优先级、待确认问题 |
| 出口 | 验收标准可测试；待确认问题已由用户回答 |

## 步骤 2：技术方案

| 项 | 说明 |
|---|---|
| 责任 | architect-agent |
| 输出 | `docs/design/DESIGN-*.md`：方案、接口契约（前后端+LLM 输入输出 JSON）、数据模型与 Alembic 步骤、三份任务包（含依赖顺序与验收标准）、风险 |
| 出口 | 契约完整三方可对齐；任务包目录互斥；用户已确认 DESIGN |

## 步骤 3：并行实现

| 项 | 说明 |
|---|---|
| 责任 | backend / frontend / ai 三个 agent，按任务包依赖顺序开工（一般：DDL 与契约先行 → 前后端并行；LLM 能力先行或与后端并行，视任务而定） |
| 各自验收 | backend：ruff + 应用可启动 + `/docs` 自测新接口；frontend：`pnpm lint` + `pnpm build`；ai：小样本真实调用通过、JSON 可解析、token 消耗已记录 |
| 出口 | 各自变更说明已交付；发现的 DESIGN 偏差——小偏差自行处理并记录，**契约级偏差回 architect 更新 DESIGN 再继续** |

## 步骤 4：评审

| 项 | 说明 |
|---|---|
| 责任 | reviewer-agent（只读） |
| 输入 | 变更集 + DESIGN + CLAUDE.md |
| 输出 | 评审报告：总结论（可合入/修复后可合入/阻断）+ 问题列表（文件:行号、severity、建议） |
| 出口 | blocker/major 清零或经用户豁免 |

## 步骤 5：修复与复审

问题按归属分发回对应开发 agent；修复后 reviewer 复审核销；结论"可提交"。

## 步骤 6：提交

| 项 | 说明 |
|---|---|
| 规则 | 在 `feature/<功能名>` 分支提交；`type(scope): 中文描述`，scope ∈ web/server/ai/docs；跨栈变更拆多个提交；`git diff` 核对后才 commit |
| 禁止 | 提交 `.env`、`uploads/`、构建产物、密钥；`--no-verify`、强推 |

## 流程出口

提交完成；若本次变更改变了架构/业务事实，责任 agent 已更新 `.claude/memory/`。

## 回退机制

- 任一步骤发现**方案级**缺陷：停止，回 architect（或 product）修正文档再入流。
- 用户在任何步骤可否决，按指示回退。
