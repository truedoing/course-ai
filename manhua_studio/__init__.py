"""
manhua-studio —— 电商素材管线（Python 课程改造 · V1 主线：去底白图）

【V1 范围】照片 → UAPI 免费抠图去底 → 白底商品图。仅 S1 一个构件，端到端可跑。
后续版本在此之上叠加：V2 场景图(S2) / V3 商品页 / V4 识别闭环(S0) / V5 工程化收口。

【运行】
    cp env.example .env      # 填 UAPI_KEY（S1 去底，免费）
    python -m manhua_studio --input 照片.jpg
（强制依赖 requests；密钥放 .env，.gitignore 已忽略，不进提交）
"""
from dotenv import load_dotenv
from pathlib import Path

_env_path = next(
    (p for p in (Path(__file__).resolve().parent / ".env", Path.cwd() / ".env") if p.exists()),
    None,
)
if _env_path is not None:
    load_dotenv(_env_path, override=False)

__version__ = "1.0"
