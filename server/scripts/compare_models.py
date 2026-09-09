#!/usr/bin/env python
"""文本模型小样本选型对比（PLAN §8 M0 验收项）。

对每个候选模型，用 `server/prompts/m0/sample_question_gen.md` 对 2 段不同材料
各出题一次（json_schema 结构化输出），记录：JSON 是否一次通过校验（重试次数）、
题目质量粗评（字段齐全度/答案是否落在选项内等简单启发式）、耗时、token 用量；
结果打印对比表并写入 `server/scripts/out/model_compare_<日期>.md`。

用法（在 server/ 目录）：
    .venv/bin/python scripts/compare_models.py [模型名 ...]
    .venv/bin/python scripts/compare_models.py --help

默认候选 glm-4-plus glm-4-air glm-4-flash。智谱在售型号随时间调整，请先到
模型广场 https://open.bigmodel.cn/modelcenter 或定价页 https://bigmodel.cn/pricing
确认当前可用型号，再用位置参数覆盖默认列表，例如：
    .venv/bin/python scripts/compare_models.py glm-4.6 glm-4.5-air glm-4-flash

成本提示：每模型 2 次调用（每次约 1-2k tokens），3 个候选约 6-12k tokens。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pydantic import BaseModel

# 让 `app` 包可导入（脚本位于 server/scripts/ 下，server/ 是包根）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai import LLMClient, LLMError, load_prompt  # noqa: E402
from app.core.config import get_settings  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPTS_DIR / "out"

DEFAULT_MODELS = ["glm-4-plus", "glm-4-air", "glm-4-flash"]

KEY_GUIDANCE = """
[跳过真实调用] ZHIPU_API_KEY 未配置或仍是占位符（sk-xxx）。
请编辑项目根 /Users/jaclyn/Desktop/ESG-proj/EN-learning/.env 中的 ZHIPU_API_KEY= 一行
（约第 3 行），填入智谱 API key 后重跑本脚本。
"""

# 两段不同主题的短材料（选小样本，控制 token 成本）
PASSAGES: list[tuple[str, str]] = [
    (
        "P1",
        "Tea is one of the most widely consumed beverages in the world, yet few people "
        "know how it was discovered. According to a Chinese legend, Emperor Shen Nong "
        "discovered tea by accident around 2737 BC, when a few leaves from a wild tea "
        "tree drifted into his pot of boiling water. Intrigued by the pleasant aroma, "
        "he tasted the infusion and found it refreshing. From China, tea gradually "
        "spread along trade routes to Japan, Europe and beyond, becoming a drink that "
        "shapes ceremonies, economies and daily habits alike.",
    ),
    (
        "P2",
        "Remote work has moved from a temporary measure to a permanent option for many "
        "companies. Supporters argue that skipping the commute saves hours every week "
        "and that employees concentrate better without office noise. Critics, however, "
        "point to weaker teamwork and the risk of loneliness. Interestingly, several "
        "studies suggest that the outcome depends less on where people work than on how "
        "deliberately managers communicate: teams that set clear goals and hold short "
        "daily check-ins tend to perform well wherever their members sit.",
    ),
]


class ChoiceQuestion(BaseModel):
    """单选题契约（与 sample_question_gen.md 的输出一致）。"""

    type: str
    stem: str
    options: list[str]
    answer: str
    analysis: str


class QuestionSet(BaseModel):
    questions: list[ChoiceQuestion]


def _key_problem(key: str) -> bool:
    """key 为空或仍是占位符 sk-xxx 时视为不可用。"""
    return not key or key.strip().startswith("sk-xxx")


def grade_question_set(qs: QuestionSet) -> tuple[int, int, list[str]]:
    """质量粗评（简单启发式，非人工质量结论）。返回 (通过检查数, 总检查数, 问题列表)。"""
    passed, total, notes = 0, 0, []

    def check(ok: bool, bad: str) -> None:
        nonlocal passed, total
        total += 1
        if ok:
            passed += 1
        else:
            notes.append(bad)

    check(len(qs.questions) == 2, f"生成 {len(qs.questions)} 题（要求 2 题）")
    for i, q in enumerate(qs.questions, 1):
        check(len(q.options) == 4, f"第{i}题选项数 {len(q.options)}≠4")
        check(len(q.options) > 1 and len(set(q.options)) == len(q.options), f"第{i}题存在重复选项")
        check(bool(q.stem.strip()), f"第{i}题题干为空")
        check(q.answer in q.options, f"第{i}题 answer 未原样出现在 options 中")
        check(len(q.analysis.strip()) >= 10, f"第{i}题解析过短")
    return passed, total, notes


@dataclass
class RunResult:
    """一次（模型 × 材料）出题调用的记录。"""

    model: str
    passage: str
    ok: bool
    retries: int = 0
    score: str = "-"
    notes: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    sample: str = ""  # 第一道题的 题干/answer/解析 摘要，供人工抽查质量
    error: str = ""


def run_one(model: str, tag: str, passage: str) -> RunResult:
    client = LLMClient(model=model)  # 每个候选模型独立客户端（覆盖 .env 的 LLM_MODEL）
    prompt = load_prompt("m0/sample_question_gen.md", passage=passage)
    result = RunResult(model=model, passage=tag, ok=False)
    start = time.perf_counter()
    try:
        raw = client.chat([{"role": "user", "content": prompt}], json_schema=QuestionSet)
    except LLMError as exc:
        result.error = str(exc)
        return result
    finally:
        result.elapsed_s = time.perf_counter() - start

    qs = QuestionSet.model_validate(json.loads(raw))
    passed, total_checks, notes = grade_question_set(qs)
    result.ok = True
    result.retries = client.last_attempts - 1
    result.score = f"{passed}/{total_checks}"
    result.notes = notes
    result.input_tokens = client.last_usage.get("input_tokens", 0)
    result.output_tokens = client.last_usage.get("output_tokens", 0)
    first = qs.questions[0]
    options = " | ".join(first.options)
    result.sample = (
        f"{first.stem}\n  选项：{options}\n  answer：{first.answer}\n  解析：{first.analysis}"
    )
    return result


def print_table(results: list[RunResult]) -> None:
    cols = [
        ("模型", 16), ("样本", 4), ("结果", 6), ("重试", 4),
        ("质量粗评", 8), ("耗时s", 7), ("tokens(in/out)", 18),
    ]
    header = " ".join(f"{name:<{width}}" for name, width in cols)
    print("\n" + header)
    print("-" * len(header))
    for r in results:
        tokens = f"{r.input_tokens}/{r.output_tokens}" if r.ok else "-"
        cells = [
            (r.model, 16), (r.passage, 4), ("OK" if r.ok else "FAIL", 6),
            (str(r.retries) if r.ok else "-", 4), (r.score if r.ok else "-", 8),
            (f"{r.elapsed_s:.1f}", 7), (tokens, 18),
        ]
        row = " ".join(f"{str(v):<{w}}" for v, w in cells)
        if not r.ok:
            row += "  " + r.error.splitlines()[0][:60]
        print(row)


def write_report(results: list[RunResult], models: list[str]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"model_compare_{date.today().isoformat()}.md"
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)
    lines = [
        "# 文本模型小样本选型（M0）",
        "",
        f"- 日期：{date.today().isoformat()}；候选：{', '.join(models)}",
        "- 任务：`m0/sample_question_gen.md` 对 2 段材料各生成 2 道单选题（结构化输出）",
        "- 质量粗评：字段齐全度/选项唯一/answer 落在 options 内等 11 项启发式检查（非人工结论）",
        f"- 汇总 token：input={total_in} output={total_out} total={total_in + total_out}",
        "",
        "| 模型 | 样本 | 结果 | 重试 | 质量粗评 | 耗时(s) | tokens(in/out) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        if r.ok:
            lines.append(
                f"| {r.model} | {r.passage} | OK | {r.retries} | {r.score} "
                f"| {r.elapsed_s:.1f} | {r.input_tokens}/{r.output_tokens} |"
            )
        else:
            lines.append(f"| {r.model} | {r.passage} | FAIL | - | - | {r.elapsed_s:.1f} | - |")
    lines += ["", "## 明细（问题与失败原因）", ""]
    for r in results:
        if r.ok and r.notes:
            lines.append(f"- {r.model}/{r.passage}（{r.score}）：{'；'.join(r.notes)}")
    lines += ["", "## 样例题目（每次运行的第一题，供人工抽查）", ""]
    for r in results:
        if r.ok:
            lines.append(f"### {r.model} / {r.passage}\n\n{r.sample}\n")
        elif not r.ok:
            lines.append(f"- {r.model}/{r.passage} 失败：{r.error}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="文本模型小样本选型：同一段材料逐模型出题，比较 JSON 遵从度/质量/耗时/token",
        epilog=(
            "模型名以智谱在售型号为准：到 https://open.bigmodel.cn/modelcenter（模型广场）"
            "或 https://bigmodel.cn/pricing（定价页）确认后，用位置参数覆盖默认列表，例如：\n"
            "  python scripts/compare_models.py glm-4.6 glm-4.5-air glm-4-flash"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "models", nargs="*", default=DEFAULT_MODELS,
        help=f"候选模型名列表（默认：{' '.join(DEFAULT_MODELS)}）",
    )
    args = parser.parse_args()
    models = args.models or DEFAULT_MODELS

    settings = get_settings()
    if _key_problem(settings.ZHIPU_API_KEY):
        print(KEY_GUIDANCE)
        return 1

    print(f"候选模型：{', '.join(models)}")
    print(f"材料：{len(PASSAGES)} 段 × 每模型，共 {len(models) * len(PASSAGES)} 次调用"
          f"（预计每次 1-2k tokens，总计约 {len(models) * len(PASSAGES) * 2}k tokens）")

    results: list[RunResult] = []
    for model in models:
        for tag, passage in PASSAGES:
            print(f"运行 {model} / {tag} ...", flush=True)
            results.append(run_one(model, tag, passage))

    print_table(results)
    report = write_report(results, models)
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)
    print(f"\n[汇总] token：input={total_in} output={total_out} total={total_in + total_out}")
    print(f"[报告] 已写入 {report}")
    ok_all = all(r.ok for r in results)
    print("[OK] 全部模型调用成功。" if ok_all else "[WARN] 存在失败调用，见上表 FAIL 行。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
