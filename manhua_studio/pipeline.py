# pipeline.py · 业务管线层（V3 引入：任务展开/质检判定/WebP/归档/交付；V5 加 pick_best）
# 不直接碰网络（网络在 adapters.py），换内部流程只动这里。
import csv
import json
from pathlib import Path

from PIL import Image  # 教学标准依赖：V3 引入 WebP 压缩

from .adapters import _ensure_dir
from .prompts import build_scene_prompt


# 构件 0 需求解析 + 构件 3 任务展开
def expand_tasks(products):
    """一个真实产品 → 展开成 N 条场景生成任务（S2 展开单元）。"""
    tasks = []
    for p in products:
        scenes = p.get("scenes") or ["北欧客厅场景", "办公桌使用场景", "礼品盒包装场景"]
        for scene in scenes:
            tasks.append({
                "sku_code": p["sku_code"],
                "name": p["name"],
                "category": p.get("category", "未分类"),
                "selling_point": p.get("selling_point", ""),
                "platform": p.get("platform", "淘宝"),
                "shot_type": "场景图",
                "angle": scene,
                "input_path": p.get("input_path"),
                "status": "pending",
            })
    return tasks


# 构件 1 状态判定
def count_status(tasks):
    """统计任务状态。"""
    return {
        "done": sum(1 for t in tasks if t["status"] == "done"),
        "failed": sum(1 for t in tasks if t["status"] == "failed"),
        "pending": sum(1 for t in tasks if t["status"] == "pending"),
    }


# 构件 11 出图后处理：WebP 压缩
WEBP_MAX_W = 1280        # 商品图网络展示够用；再大只浪费带宽
WEBP_QUALITY = 82        # WebP 有损质量；80~85 肉眼几乎无损，体积最优


def stage_optimize_web(paths, max_w=WEBP_MAX_W, quality=WEBP_QUALITY):
    """把生成的 PNG/JPG 统一转 WebP + 限制最大边 + 删原文件回收空间。"""
    mapping = {}
    for src in paths:
        sp = Path(src)
        if not sp.exists():
            continue
        im = Image.open(sp)
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        if im.width > max_w:
            h = round(im.height * max_w / im.width)
            im = im.resize((max_w, h), Image.LANCZOS)
        out = sp.with_suffix(".webp")
        im.save(out, "WEBP", quality=quality, method=6, optimize=True)
        if out.exists() and out.stat().st_size > 0:
            old_kb = round(sp.stat().st_size / 1024)
            new_kb = round(out.stat().st_size / 1024)
            sp.unlink()
            mapping[str(sp)] = str(out)
            print(f"[优化] {sp.name} {old_kb}KB -> {out.name} {new_kb}KB")
    return mapping


# 构件 5 归档 + 构件 10 交付 + S3+ 数据化交付
def archive_run(tasks, run_dir="deliverables/runs"):
    """跑批结果归档成 production_log.csv（跨组交接'别人能看懂'的凭据）。"""
    _ensure_dir(run_dir)
    log_path = Path(run_dir) / "production_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sku_code", "name", "platform", "shot_type", "scene",
                    "status", "cost", "path", "error"])
        for t in tasks:
            w.writerow([t["sku_code"], t["name"], t["platform"], t["shot_type"], t["angle"],
                        t["status"], t.get("cost", ""), t.get("path", ""), t.get("error", "")])
    return log_path


def deliver(tasks, kept, rejected, product, out_dir="deliverables"):
    """构件 10：按 SKU 分文件夹归档 + 废片率统计 + README。"""
    out = Path(out_dir)
    _ensure_dir(out)
    for t in kept:
        sku_dir = out / t["sku_code"]
        _ensure_dir(sku_dir)
        fname = f"{t['name']}_{t['shot_type']}_{t['angle']}.json"
        (sku_dir / fname).write_text(json.dumps({
            "sku_code": t["sku_code"], "platform": t["platform"],
            "shot_type": t["shot_type"], "scene": t["angle"],
            "path": t.get("path"), "ai_synthetic": True,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    total = len(tasks)
    scrap_rate = round(len(rejected) / total, 3) if total else 0
    readme = out / "README.md"
    readme.write_text(
        f"# 交付物 · {product._name} 素材管线（V3 商品页：UAPI 抠图 + Seedream 4.0 场景化）\n\n"
        f"- 合格素材：{len(kept)} 张\n"
        f"- 废片（含失败）：{len(rejected)} 张，废片率 {scrap_rate}\n"
        f"- 运行：python -m manhua_studio --input <照片>\n\n"
        f"## 合规须知（教学必讲）\n"
        f"- 本批图片均由 AI 生成，上架须标注「AI合成」。\n"
        f"- 真实产品 + AI 扩展图 = 合法合规展示素材；纯文本编造实物直接上架属虚假宣传，红线不碰。\n",
        encoding="utf-8")
    return readme


def write_sku_data(product, all_tasks):
    """S3+ 数据化交付：把文案 + 实际出图路径写成 SKU JSON/JSONP。"""
    sku_tasks = [t for t in all_tasks if t["sku_code"] == product["sku_code"]]
    kept = [t for t in sku_tasks if t["status"] == "done"]
    images = []
    raw = product.get("input_path")
    if raw:
        images.append({"src": raw, "caption": "① 实拍原图", "kind": "raw", "detail": ""})
    white = product.get("white_path")
    if white:
        images.append({"src": white, "caption": "② 白底主图 · S1 UAPI 去底", "kind": "white", "detail": ""})
    for t in kept:
        images.append({"src": t["path"], "caption": f"场景图 · {t['angle']}", "kind": "scene", "detail": ""})
    meta = {
        "sku_code": product["sku_code"],
        "product_name": product["name"],
        "shop_name": product.get("shop_name", "演示小铺"),
        "price": 39.00,
        "currency": "¥",
        "images": images,
    }
    out_dir = Path("deliverables") / product["sku_code"]
    _ensure_dir(out_dir)
    (out_dir / "sku.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "sku.js").write_text(
        "window.SKU = " + json.dumps(meta, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"[交付] 已写数据驱动文件: {out_dir}/sku.json + sku.js")
    return out_dir
