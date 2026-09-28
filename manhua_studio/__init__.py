"""
manhua-studio —— 电商素材管线（Python 课程改造 · V2 主线：场景图）

【V2 范围】在 V1 去底白底之上，加 S2 场景化出图（Seedream 4.0 参考图生图）+ prompts 模板。
一张白底图 → 2–3 张场景图。任务展开/重试暂在 cli.py，V3 起移入 pipeline.py。

【运行】
    cp env.example .env      # 填 UAPI_KEY（S1）+ ARK_API_KEY（S2）
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

__version__ = "2.0"
