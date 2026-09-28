# cli.py · 入口（V4：S0 识别闭环 → 照片丢入全自动出全套）
import os
import argparse
from pathlib import Path

from .schemas import GenerationError, Product
from .adapters import stage0_recognize, stage1_remove_bg, generate_image
from .prompts import DEFAULT_SCENES
from .pipeline import (expand_tasks, count_status, stage_optimize_web,
                       archive_run, deliver, write_sku_data)


def run_batch(tasks, max_retry=3, api_key=None, white_path=None):
    for t in tasks:
        for attempt in range(1, max_retry + 1):
            try:
                res = generate_image(t, api_key=api_key, white_path=white_path)
                t["status"] = "done"
                t["path"] = res.get("path")
                t["cost"] = res.get("cost", 0.0)
                break
            except GenerationError as e:
                t["status"] = "failed" if attempt == max_retry else "pending"
                t["error"] = str(e)
    return tasks


def main():
    parser = argparse.ArgumentParser(description="manhua V4：照片 → S0 识别 → 全自动出全套")
    parser.add_argument("--input", required=True, help="商品照片路径")
    args = parser.parse_args()

    ark_key = os.getenv("ARK_API_KEY")
    uapi_key = os.getenv("UAPI_KEY")
    if not Path(args.input).exists():
        raise SystemExit(f"[错误] --input 照片不存在: {args.input}")
    if not ark_key:
        raise SystemExit("[错误] 缺少 ARK_API_KEY：S0 识别 + S2 出图需要。\n       填入火山方舟密钥到 .env。")

    print("[S0] 豆包视觉识别商品并生成文案...")
    meta = stage0_recognize(args.input, ark_key)
    products = [{
        "sku_code": "SKU-001",
        "name": meta.get("product_name", "未命名商品"),
        "subtitle": meta.get("subtitle", ""),
        "selling_point": ";".join(meta.get("points", [])) or meta.get("subtitle", ""),
        "shop_name": meta.get("shop_name", "演示小铺"),
        "points": meta.get("points", []),
        "tags": meta.get("tags", ["AI 合成图"]),
        "category": "未分类",
        "platform": "淘宝",
        "input_path": args.input,
        "scenes": meta.get("suggested_scenes") or list(DEFAULT_SCENES),
    }]
    if not uapi_key:
        raise SystemExit("[错误] 缺少 UAPI_KEY：S1 去底需要。\n       去 uapis.cn 免费申请并填入 .env。")

    print(f"[解析] {len(products)} 个商品")
    all_tasks = []
    for p in products:
        print(f"[S1] UAPI 去底白底: {p['name']}")
        white = stage1_remove_bg(p["input_path"], uapi_key)
        p["white_path"] = white
        tasks = expand_tasks([p])
        print(f"[S2] 展开 {len(tasks)} 条场景任务")
        tasks = run_batch(tasks, api_key=ark_key, white_path=white)
        all_tasks += tasks

    gen_paths = [p["white_path"] for p in products if p.get("white_path")]
    gen_paths += [t["path"] for t in all_tasks if t.get("status") == "done" and t.get("path")]
    if gen_paths:
        mapping = stage_optimize_web(gen_paths)
        for p in products:
            if p.get("white_path") in mapping:
                p["white_path"] = mapping[p["white_path"]]
        for t in all_tasks:
            if t.get("path") in mapping:
                t["path"] = mapping[t["path"]]
        print(f"[优化] 压缩 {len(mapping)} 张")

    print("[状态]", count_status(all_tasks))
    archive_run(all_tasks)

    kept = [t for t in all_tasks if t["status"] == "done"]
    rejected = [t for t in all_tasks if t["status"] != "done"]
    prod = Product(products[0]["name"], "", "ref.png", 42)
    readme = deliver(all_tasks, kept, rejected, prod)
    print(f"[交付] {readme}")
    for p in products:
        write_sku_data(p, all_tasks)


if __name__ == "__main__":
    main()
