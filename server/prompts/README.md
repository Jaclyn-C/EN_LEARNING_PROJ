# prompts/ — LLM prompt 模板（ai-agent 主场）

本目录存放所有 LLM prompt 模板文件，由 `app/ai/prompt_loader.py` 的 `load_prompt()` 加载渲染。

## 约定（依据 CLAUDE.md §6）

- **模板文件化**：prompt 一律为模板文件（变量占位），由 `app/ai/` 代码加载渲染；
  禁止在业务代码中内联 prompt。
- **占位语法**：`str.format` 风格 `{var}`（不引入 Jinja2）。模板中的**字面大括号**
  必须转义为 `{{` `}}`（如 JSON 输出示例），渲染后还原为单个大括号。
- **版本化**：模板改动视为行为变更，文件头部注释标注版本与日期
  （`<!-- 路径 | v版本 日期 | 用途 | 变量 -->`）；涉及出题/批改大改时同步更新
  `.claude/memory/` 对应文档。
- **命名**：按里程碑/场景分子目录，`<场景>_<用途>.md`（如 `m0/smoke_chat.md`、
  `question_gen.md`、`grading.md`）。
- 业务代码只依赖 `app/ai/` 门面，不直接读本目录。

## 现有模板

- `m0/smoke_chat.md`：冒烟——普通对话（变量 `{topic}`）。
- `m0/smoke_json.md`：冒烟——json_schema 结构化输出（变量 `{word}`，输出
  word/phonetic/meaning/example 四字段）。
- `m0/sample_question_gen.md`：文本模型选型——按材料生成 2 道单选题 JSON
  （变量 `{passage}`，输出 questions[].{type,stem,options,answer,analysis}）。
