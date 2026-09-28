"""
manhua-studio —— 电商素材管线（Python 课程改造 · V3 主线：商品页）

【V3 范围】在 V2 场景图之上，加数据化(sku.json/js) + 商品页 + WebP 压缩 + 学号定位。
引入 pipeline.py（任务展开/质检判定/WebP/归档/交付）与 Product 类（OOP 枢纽）。
这是"像真家伙"的商品页成型的版本。

【运行】
    cp env.example .env      # 填 UAPI_KEY（S1）+ ARK_API_KEY（S2）
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

__version__ = "3.0"
