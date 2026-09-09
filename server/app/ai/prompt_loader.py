"""prompt 模板加载器：从 `server/prompts/` 读模板并渲染 `{var}` 占位（CLAUDE.md §6）。

约定：
- 模板为纯文本文件（.md），`str.format` 风格占位（如 `{topic}`），不引入 Jinja2；
- 模板中的**字面大括号**必须转义写成 `{{` `}}`（如 JSON 输出示例），渲染后还原；
- 支持子目录：`load_prompt("m0/smoke_chat.md")`；禁止 `..` 逃逸出 prompts/；
- prompt 一律放本目录，业务代码只调 `load_prompt`，禁止内联大段 prompt。
"""

from pathlib import Path

# server/app/ai/prompt_loader.py 上溯两级 = server/，prompts 与 app 平级
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(name: str, **variables: object) -> str:
    """读取模板 `server/prompts/<name>` 并渲染变量，返回最终 prompt 字符串。

    抛错：
    - `FileNotFoundError`：模板不存在（附现有模板清单）或路径逃逸；
    - `KeyError` / `IndexError`：模板存在未提供（或多余占位符缺失）的变量。
    """
    path = (PROMPTS_DIR / name).resolve()
    if not path.is_relative_to(PROMPTS_DIR.resolve()):
        raise FileNotFoundError(f"非法模板路径 {name!r}：不允许逃逸出 {PROMPTS_DIR}")
    if not path.is_file():
        available = sorted(
            str(p.relative_to(PROMPTS_DIR)) for p in PROMPTS_DIR.rglob("*.md") if p.is_file()
        )
        listing = ", ".join(available) if available else "（无）"
        raise FileNotFoundError(
            f"prompt 模板不存在：{PROMPTS_DIR / name}（现有模板：{listing}）"
        )
    text = path.read_text(encoding="utf-8")
    try:
        return text.format(**variables)
    except (KeyError, IndexError) as exc:
        given = sorted(variables)
        raise KeyError(
            f"模板 {name} 的占位符与传入变量不匹配（{exc}；已传入变量：{given}）"
        ) from exc
