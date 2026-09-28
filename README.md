# course-ai · AI 原生课程大体系

工艺美术类高职计算机专业 · AI 原生课程改造。

本仓库是「课程大体系」的容器。其中 `manhua_studio` 是 **Python 方向的工程线**（电商素材出图管线），是当前重点建设对象；其余课程参考资料归入 `doc/`。

## 目录分层

- `manhua_studio/` — Python 教学代码包（学生实际运行 / 修改的对象）
  - `docs/` — 该工程专属教学文档（三种走法说明页、教师参考、反思单、迭代计划等 7 份）
  - `cli.py` / `adapters.py` / `pipeline.py` / `prompts.py` / `schemas.py` — 代码
- `doc/` — 课程大体系参考资料（AIGC 赛道、JS/Python 就业分析、三级火箭、电商与商品页样例、执行基线等 25 份 HTML）+ 引用图 `doc/assets/`
- `env.example` — 密钥模板（复制为 `.env` 填 `UAPI_KEY` / `ARK_API_KEY`，不进库）

> `manhua_studio` 只是本仓库的一个子包，git 与运行都以仓库根（父级 `course-ai`）为工作区。

## 运行 manhua_studio（Python 工程）

在仓库根目录（即包含 `manhua_studio/` 的这一层）执行：

```bash
cp env.example .env        # 填好 UAPI_KEY / ARK_API_KEY
python -m manhua_studio --input 你的商品照片.jpg
```

> 以「包方式」运行（`python -m manhua_studio`），不要用 `python manhua_studio/cli.py`（包内相对导入会报 `ImportError`）。
> 密钥集中放本机 `.env`，不进代码、不进提交（`.gitignore` 已忽略）。

## 版本管理（manhua_studio 的 V1–V5 演进）

一套代码 + `git tag` 标记阶段版本，每版端到端可跑、是完整的（范围由小到大，老代码原样保留）：

| 版本 | 范围 | 新增构件 |
|---|---|---|
| v1 | 去底白图 | S1 去底 + cli 入口 |
| v2 | 场景图 | S2 出图 + prompts 模板 |
| v3 | 商品页 | 数据化(sku) + 商品页 + WebP + 学号 |
| v4 | 识别闭环 | S0 自动识别（照片→全自动出全套） |
| v5 | 工程化收口 | 质检筛选 + 错误处理 + 归档日志 |

`git checkout vN` 回到第 N 阶段整库快照（代码 + 当时教学文档都在）。
