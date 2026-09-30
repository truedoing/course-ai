# =====================================================================
# cli.py · 入口：解析参数、调度管线（业务逻辑在 adapters/pipeline，不在本文件）
#
# 构件 4 · 封装调用：本文件只做参数解析与调度，真实能力封装在
#               adapters/pipeline，便于按章增量（每章只新增/启用一个构件函数）。
#
# 用法：
#   python -m manhua_studio --input 照片.jpg
#
# 参数：
#   --input   商品照片（S1 去底 + S2 出图均使用此照片）
#
# 依赖 key（缺失即报错退出）：
#   UAPI_KEY    S1 去底白底（uapis.cn 免费）
#   ARK_API_KEY S0 识别 + S2 出图（火山方舟）
# =====================================================================
import os
import time
import argparse
from pathlib import Path

from .schemas import GenerationError, Product, Character
from .adapters import (
    stage0_recognize, stage1_remove_bg, generate_image,
)
from .prompts import DEFAULT_SCENES
from .pipeline import (
    expand_tasks, count_status, pick_best,
    archive_run, deliver, write_sku_data, stage_optimize_web,
)


# 构件 7 · 重试：真实 API 偶发失败自动重试，整批不因个别失败归零。
def run_batch(tasks, max_retry=3, api_key=None, white_path=None):
    for t in tasks:
        for attempt in range(1, max_retry + 1):
            try:
                res = generate_image(t, api_key=api_key, white_path=white_path)
                t["status"] = "done"
                t["seed"] = res.get("seed")
                t["metrics"] = res.get("metrics")
                t["path"] = res.get("path")
                t["cost"] = res.get("cost", 0.0)
                break
            except GenerationError as e:
                t["status"] = "failed" if attempt == max_retry else "pending"
                t["error"] = str(e)
    return tasks


def main():
    parser = argparse.ArgumentParser(
        description="manhua 电商出图管线：照片 -> 白底 -> 场景图 -> 商品页（需外部服务 key）")
    parser.add_argument("--input", required=True,
                        help="商品照片路径（去底与出图均使用此照片）")
    args = parser.parse_args()

    ark_key = os.getenv("ARK_API_KEY")
    uapi_key = os.getenv("UAPI_KEY")

    if not Path(args.input).exists():
        raise SystemExit(f"[错误] --input 照片不存在: {args.input}")

    if not ark_key:
        raise SystemExit(
            "[错误] 缺少 ARK_API_KEY：S0 识别 + S2 出图需要。\n"
            "       请先 cp env.example .env 并填入火山方舟密钥。")
    print("[S0] 豆包视觉识别商品并生成文案（名称/卖点/建议场景）...")
    meta = stage0_recognize(args.input, ark_key)
    products = [{
        "sku_code": "SKU-001",
        "name": meta.get("product_name", "未命名商品"),
        "subtitle": meta.get("subtitle", ""),
        "selling_point": ";".join(meta.get("points", [])) if meta.get("points") else meta.get("subtitle", ""),
        "shop_name": meta.get("shop_name", "演示小铺"),
        "points": meta.get("points", []),
        "tags": meta.get("tags", ["AI 合成图"]),
        "category": "未分类",
        "platform": "淘宝",
        "input_path": args.input,
        "scenes": meta.get("suggested_scenes") or list(DEFAULT_SCENES),
    }]

    if not uapi_key:
        raise SystemExit(
            "[错误] 缺少 UAPI_KEY：S1 去底白底需要。\n"
            "       去 uapis.cn 免费申请，填入 .env 的 UAPI_KEY。")

    t0 = time.time()
    all_tasks = []
    print(f"[解析] {len(products)} 个商品")

    for p in products:
        print(f"[S1] UAPI 免费抠图去底白底: {p['name']}")
        white = stage1_remove_bg(p["input_path"], uapi_key)
        p["white_path"] = white
        tasks = expand_tasks([p])
        print(f"[S2] 展开 {len(tasks)} 条场景任务（{p['name']}）")
        tasks = run_batch(tasks, api_key=ark_key, white_path=white)
        all_tasks += tasks

    # 构件 10 · 出片交付：统一压成 WebP（出图后处理）
    gen_paths = []
    for p in products:
        if p.get("white_path"):
            gen_paths.append(p["white_path"])
    for t in all_tasks:
        if t.get("status") == "done" and t.get("path"):
            gen_paths.append(t["path"])
    if gen_paths:
        mapping = stage_optimize_web(gen_paths)
        for p in products:
            if p.get("white_path") in mapping:
                p["white_path"] = mapping[p["white_path"]]
        for t in all_tasks:
            if t.get("path") in mapping:
                t["path"] = mapping[t["path"]]
        print(f"[优化] 共压缩 {len(mapping)} 张生成图 -> WebP")

    print("[状态]", count_status(all_tasks))
    archive_run(all_tasks)

    kept_all, rejected_all = [], []
    for p in products:
        sku_tasks = [t for t in all_tasks if t["sku_code"] == p["sku_code"]]
        if p["category"] == "漫剧角色":
            prod = Character(p["name"], "", "ref_aci.png", 7)
        else:
            prod = Product(p["name"], "", "ref.png", 42)
        kept, rejected = pick_best(sku_tasks, prod)
        kept_all += kept
        rejected_all += rejected
        print(f"  {p['name']}: 合格 {len(kept)} / 废片 {len(rejected)}")

    first = products[0]
    if first["category"] == "漫剧角色":
        readme_product = Character(first["name"], "", "ref.png", 0)
    else:
        readme_product = Product(first["name"], "", "ref.png", 0)
    readme = deliver(all_tasks, kept_all, rejected_all, readme_product)
    print(f"[交付] {readme}  耗时 {round(time.time()-t0, 2)}s")

    for p in products:
        write_sku_data(p, all_tasks)


if __name__ == "__main__":
    main()
