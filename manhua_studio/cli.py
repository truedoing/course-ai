# cli.py · 入口（V2：去底白图 + 场景图；任务展开/重试在本文件，V3 起移入 pipeline.py）
import os
import argparse
from pathlib import Path

from .schemas import GenerationError
from .adapters import stage1_remove_bg, generate_image
from .prompts import DEFAULT_SCENES


def expand_tasks(product):
    """一个商品 → 展开成 N 条场景生成任务（S2 展开单元）。"""
    tasks = []
    scenes = product.get("scenes") or list(DEFAULT_SCENES)
    for scene in scenes:
        tasks.append({
            "sku_code": product["sku_code"],
            "name": product["name"],
            "selling_point": product.get("selling_point", ""),
            "platform": product.get("platform", "淘宝"),
            "shot_type": "场景图",
            "angle": scene,
            "input_path": product.get("input_path"),
            "status": "pending",
        })
    return tasks


def run_batch(tasks, max_retry=3, api_key=None, white_path=None):
    """构件 7 · 重试：真实 API 偶发失败自动重试。"""
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
    parser = argparse.ArgumentParser(description="manhua V2：照片 → 白底 → 场景图")
    parser.add_argument("--input", required=True, help="商品照片路径")
    args = parser.parse_args()

    ark_key = os.getenv("ARK_API_KEY")
    uapi_key = os.getenv("UAPI_KEY")
    if not Path(args.input).exists():
        raise SystemExit(f"[错误] --input 照片不存在: {args.input}")
    if not uapi_key:
        raise SystemExit("[错误] 缺少 UAPI_KEY：S1 去底需要。\n       去 uapis.cn 免费申请并填入 .env。")
    if not ark_key:
        raise SystemExit("[错误] 缺少 ARK_API_KEY：S2 出图需要。\n       填入火山方舟密钥到 .env。")

    name = Path(args.input).stem
    product = {
        "sku_code": "SKU-001",
        "name": name,
        "selling_point": "",
        "platform": "淘宝",
        "input_path": args.input,
        "scenes": list(DEFAULT_SCENES),
    }
    print(f"[S1] UAPI 去底白底: {name}")
    white = stage1_remove_bg(args.input, uapi_key)
    product["white_path"] = white
    tasks = expand_tasks(product)
    print(f"[S2] 展开 {len(tasks)} 条场景任务")
    tasks = run_batch(tasks, api_key=ark_key, white_path=white)
    done = sum(1 for t in tasks if t["status"] == "done")
    print(f"[完成] 白底图: {white}；场景图 {done}/{len(tasks)} 张")


if __name__ == "__main__":
    main()
