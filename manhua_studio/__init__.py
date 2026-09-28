"""
manhua-studio —— 电商素材管线（Python 课程改造 · V4 主线：识别闭环）

【V4 范围】在 V3 之上，加 S0 智能识别（豆包视觉）：照片丢入 → 自动识别商品名/卖点/场景 → 全自动出全套。
这是"闭环"成型的版本——学生只需拍一张照片。

【运行】
    cp env.example .env      # 填 UAPI_KEY（S1）+ ARK_API_KEY（S0+S2）
    python -m manhua_studio --input 照片.jpg
（强制依赖 requests + Pillow；密钥放 .env，.gitignore 已忽略，不进提交）
"""
from dotenv import load_dotenv
from pathlib import Path

_env_path = next(
    (p for p in (Path(__file__).resolve().parent / ".env", Path.cwd() / ".env") if p.exists()),
    None,
)
if _env_path is not None:
    load_dotenv(_env_path, override=False)

__version__ = "4.0"
