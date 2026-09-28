"""
manhua-studio —— 电商素材管线（Python 课程改造 V5 主线 · 工程化收口 · 真实闭环）

【真实闭环（V5，工程化收口）】
学生拍一张真实产品照片（S0 豆包视觉识别）→ UAPI 免费抠图去底白底（S1）→
Seedream 4.0 参考图场景化/多版本（S2）→ 质检筛选 + WebP 压缩 + 标注"AI合成" + 归档日志（V3/V5）。
这是当下 AI 电商出图的真实工业流程，全 API / 薅免费额度，不碰本地模型。

【版本演进（git tag）】V1 去底白图 → V2 场景图 → V3 商品页 → V4 识别闭环 → V5 工程化收口。
每版端到端可跑、是完整的，老代码原样保留；git checkout vN 回看第 N 阶段整库快照。

【工程结构（入口薄 / 引擎厚 / 适配器与管线两层）】
    cli.py             —— 入口：只解析参数、调度，不写业务
    adapters.py        —— 外部服务适配层：HTTP + S0 识别 + S1 去底 + S2 出图
    pipeline.py        —— 业务管线层：需求解析/任务展开/质检/WebP/归档交付
    schemas.py         —— 数据结构：Product / Character / 异常集中定义
    prompts.py         —— 平台规范 + 提示词模板（并跑档主要改这里）
    .env —— 密钥配置（python-dotenv 自动加载，不进提交）
    assets/            —— 参考图·模板（资源）
    deliverables/      —— 产物（output）
    README.md          —— 让别人能跑起来的最低要求

【重要技术事实（讲课时务必讲清）】
- S1 去底：国内免费抠图 API「UAPI / uapis.cn matting」。学生本地照片直接上传返回白底图。
- S2 场景化：Seedream 4.0（doubao-seedream-4-0-250828）参考图生图，保留产品外观生成整图。
- 所有 API 调用走 requests（强制依赖）；密钥集中放 .env，由 python-dotenv 自动加载，.gitignore 已忽略。

【合规红线（教学必讲）】
- 纯文本编造实物直接上架 = 虚假宣传，职业红线，我们不教这个。
- AI 生成的图必须标注"AI合成"（市场监管总局要求）。
- 真实产品 + AI 扩展图 = 合法合规的展示素材。

【运行】
    cp env.example .env      # 填 UAPI_KEY（S1）+ ARK_API_KEY（S0+S2）
    python -m manhua_studio --input 杯子.jpg
（强制依赖 requests + Pillow；密钥放 .env，不进提交）
"""
from dotenv import load_dotenv
from pathlib import Path

_env_path = next(
    (p for p in (Path(__file__).resolve().parent / ".env", Path.cwd() / ".env") if p.exists()),
    None,
)
if _env_path is not None:
    load_dotenv(_env_path, override=False)

__version__ = "5.0"
