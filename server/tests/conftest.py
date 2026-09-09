"""测试公共配置：在任何 app.* 导入前把 DATABASE_URL 指到独立临时 SQLite。

`app.core.db` 在模块级按 Settings 创建 engine，因此必须在导入应用前
通过环境变量覆盖（pydantic-settings 中环境变量优先于 .env），避免碰开发库。
"""

import os
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="enl-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
