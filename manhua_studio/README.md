# manhua_studio · Python 电商素材管线

工艺美术类高职 · AI 原生课程改造工程线（course-ai 大体系下的一条）。
照片 → 去底白底(S1) → 场景图(S2) → 商品页/数据化(V3) → 自动识别闭环(S0, V4) → 工程化收口(V5)。

运行（在 course-ai 仓库根目录）：
    cp env.example .env        # 填 UAPI_KEY / ARK_API_KEY
    python -m manhua_studio --input 照片.jpg

版本演进见仓库根 README.md（V1–V5）。密钥放 .env，.gitignore 已忽略，不进提交。
