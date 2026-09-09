"""ai 层离线单测：prompt 渲染 + JSON 提取/校验（不发起任何真实 LLM 调用）。"""

import pytest

from app.ai import load_prompt
from app.ai.llm_client import _extract_json, _validate_schema

# ---------------------------------------------------------------- load_prompt


def test_load_prompt_renders_vars_and_unescapes_braces() -> None:
    out = load_prompt("m0/smoke_json.md", word="resilient")
    assert "resilient" in out
    assert "{" in out and "{{" not in out  # JSON 示例的字面大括号已还原
    assert "{word}" not in out  # 占位符已被替换


def test_load_prompt_missing_variable_raises() -> None:
    with pytest.raises(KeyError, match="占位符"):
        load_prompt("m0/smoke_json.md")  # 未传 word


def test_load_prompt_missing_file_lists_available() -> None:
    with pytest.raises(FileNotFoundError, match="现有模板"):
        load_prompt("m0/no_such_template.md", x=1)


def test_load_prompt_rejects_path_escape() -> None:
    with pytest.raises(FileNotFoundError, match="逃逸"):
        load_prompt("../app/ai/llm_client.py")


# ------------------------------------------------------- _extract_json / _validate_schema


def test_extract_json_plain_and_fenced_and_noisy() -> None:
    assert _extract_json('{"a": 1}') == {"a": 1}
    assert _extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _extract_json('结果是：\n{"a": [1, 2]}\n以上。') == {"a": [1, 2]}


def test_extract_json_invalid_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _extract_json("这不是 JSON")


def test_validate_schema_subset() -> None:
    schema = {
        "type": "object",
        "required": ["word"],
        "properties": {
            "word": {"type": "string"},
            "count": {"type": "integer"},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
    }
    assert _validate_schema({"word": "hi", "count": 3, "tags": ["a"]}, schema) == []
    errors = _validate_schema({"count": True, "tags": ["a", 2]}, schema)
    assert any("word" in e for e in errors)  # 缺 required 字段
    assert any("bool" in e for e in errors)  # bool 不得冒充 integer
    assert any("[1]" in e for e in errors)  # 数组元素类型错误
