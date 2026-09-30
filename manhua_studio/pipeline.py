# =====================================================================
# pipeline.py · 业务管线层（原 engine/plan + quality + optimize + delivery）
#   这一层处理"内部业务"：需求解析、任务展开、质检筛选、WebP 压缩、归档交付。
#   不直接碰网络（网络在 adapters.py），换内部流程只动这里。
#   V5：在 V3 管线基础上加 pick_best 质检筛选（构件 9）。
# =====================================================================
import csv
import json
from pathlib import Path

from PIL import Image  # 教学标准依赖：强制安装，缺失即明确报错

from .adapters import _ensure_dir
from .prompts import build_scene_prompt


# ---------------------------------------------------------------------
# 构件 0 需求解析 + 构件 3 任务展开
# ---------------------------------------------------------------------
def parse_products_csv(path):
    """从 CSV 读取多个真实产品：列 = image,name,selling_point,category,platform,scenes"""
    products = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("name"):
                continue
            scenes = [s.strip() for s in (row.get("scenes") or "").split(",") if s.strip()]
            products.append({
                "sku_code": row.get("sku_code") or f"SKU-{len(products)+1:03d}",
                "name": row["name"].strip(),
                "category": (row.get("category") or "未分类").strip(),
                "selling_point": (row.get("selling_point") or "").strip(),
                "platform": (row.get("platform") or "淘宝").strip(),
                "input_path": (row.get("image") or "").strip(),
                "scenes": scenes,
            })
    return products


def expand_tasks(products):
    """一个真实产品 -> 展开成 N 条场景生成任务（S2 展开单元）。"""
    tasks = []
    for p in products:
        scenes = p.get("scenes") or ["北欧客厅场景", "办公桌使用场景", "礼品盒包装场景"]
        for scene in scenes:
            t = {
                "sku_code": p["sku_code"],
                "name": p["name"],
                "category": p.get("category", "未分类"),
                "selling_point": p.get("selling_point", ""),
                "platform": p.get("platform", "淘宝"),
                "shot_type": "场景图",
                "angle": scene,
                "input_path": p.get("input_path"),
                "status": "pending",
            }
            tasks.append(t)
    return tasks


# ---------------------------------------------------------------------
# 构件 1 状态判定 + 构件 9 质检筛选
# ---------------------------------------------------------------------
def count_status(tasks):
    """构件 1：统计任务状态。"""
    done = sum(1 for t in tasks if t["status"] == "done")
    failed = sum(1 for t in tasks if t["status"] == "failed")
    pending = sum(1 for t in tasks if t["status"] == "pending")
    return {"done": done, "failed": failed, "pending": pending}


def pick_best(tasks, product, threshold=0.7):
    """构件 9：按可判定标准筛选。真实模式 metrics=None -> 自动质检待二级 B4 / 人工。"""
    kept, rejected = [], []
    for t in tasks:
        if t["status"] != "done":
            rejected.append(t)
            continue
        if t.get("metrics") is None:        # 真实模式：质检待二级 B4 / 人工
            t["score"] = "QC待定"
            kept.append(t)
            continue
        score = product.score(t["metrics"])   # 多态：Product 还是 Character 自动选
        t["score"] = score
        (kept if score >= threshold else rejected).append(t)
    return kept, rejected


# ---------------------------------------------------------------------
# 构件 11 出图后处理：WebP 压缩
# ---------------------------------------------------------------------
WEBP_MAX_W = 1280
WEBP_QUALITY = 82


def stage_optimize_web(paths, max_w=WEBP_MAX_W, quality=WEBP_QUALITY):
    """把生成的 PNG/JPG 统一转 WebP + 限制最大边 + 去元数据，并删原文件回收空间。"""
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


# ---------------------------------------------------------------------
# 构件 5 归档 + 构件 10 交付 + 数据化交付
# ---------------------------------------------------------------------
def archive_run(tasks, run_dir="deliverables/runs"):
    """构件 5：跑批结果归档成 production_log.csv（跨组交接'别人能看懂'的凭据）。"""
    _ensure_dir(run_dir)
    log_path = Path(run_dir) / "production_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sku_code", "name", "platform", "shot_type", "scene",
                    "status", "seed", "bg_purity", "comp_ratio", "clarity",
                    "text_ratio", "cost", "ai_synthetic", "path", "error"])
        for t in tasks:
            m = t.get("metrics") or {}
            w.writerow([t["sku_code"], t["name"], t["platform"], t["shot_type"], t["angle"],
                        t["status"], t.get("seed", ""), m.get("bg_purity", ""),
                        m.get("comp_ratio", ""), m.get("clarity", ""), m.get("text_ratio", ""),
                        t.get("cost", ""), "AI合成" if t.get("path") else "",
                        t.get("path", ""), t.get("error", "")])
    return log_path


def deliver(tasks, kept, rejected, product, out_dir="deliverables"):
    """构件 10：按 SKU 分文件夹归档 + 废片率/成本统计 + README。"""
    out = Path(out_dir)
    _ensure_dir(out)
    for t in kept:
        sku_dir = out / t["sku_code"]
        _ensure_dir(sku_dir)
        fname = f"{t['name']}_{t['shot_type']}_{t['angle']}.json"
        (sku_dir / fname).write_text(json.dumps({
            "sku_code": t["sku_code"], "platform": t["platform"],
            "shot_type": t["shot_type"], "scene": t["angle"],
            "seed": t.get("seed"), "score": t.get("score"), "metrics": t.get("metrics"),
            "path": t.get("path"),
            "ai_synthetic": True,
            "prompt_scene": build_scene_prompt(t["name"], t["selling_point"], t["angle"]),
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(tasks)
    scrap_rate = round(len(rejected) / total, 3) if total else 0
    readme = out / "README.md"
    readme.write_text(
        f"# 交付物 · {product._name} 素材管线（真实闭环 V5 · UAPI 抠图 + Seedream 4.0 参考图场景化）\n\n"
        f"- 合格素材：{len(kept)} 张（基于真实产品照片 + UAPI 免费抠图去底 + Seedream 4.0 参考图生图）\n"
        f"- 废片（含失败）：{len(rejected)} 张，废片率 {scrap_rate}\n"
        f"- 运行：python -m manhua_studio --input <照片>\n\n"
        f"## 合规须知（教学必讲）\n"
        f"- 本批图片均由 AI 生成，**上架/对外展示须标注「AI合成」**（市场监管总局要求）。\n"
        f"- 真实产品 + AI 扩展图 = 合法合规展示素材；纯文本编造实物直接上架属虚假宣传，红线不碰。\n"
        f"- 真实模式 score='QC待定'：自动质检是二级 B4 独立步骤（人或视觉模型复核）。\n"
        f"- 每张场景图下方 manifest 含 ai_synthetic=True 与生成 prompt，便于溯源。\n",
        encoding="utf-8")
    return readme


def write_sku_data(product, all_tasks):
    """S3+ 数据化交付：把 LLM 文案 + 实际出图路径写成 SKU JSON/JSONP。"""
    sku_tasks = [t for t in all_tasks if t["sku_code"] == product["sku_code"]]
    kept = [t for t in sku_tasks if t["status"] == "done"]
    images = []
    raw = product.get("input_path")
    if raw:
        images.append({"src": raw, "caption": "① 实拍原图 · 商家随手拍（客户拍的，闭环起点）",
                       "kind": "raw", "detail": ""})
    white = product.get("white_path")
    if white:
        images.append({"src": white, "caption": "② 白底主图 · S1 UAPI 免费抠图去底",
                       "kind": "white", "detail": ""})
    for t in kept:
        prompt = t.get("prompt") or ""
        images.append({
            "src": t["path"],
            "caption": f"场景图 · {t['angle']}",
            "kind": "scene",
            "detail": (prompt[:60] + "…") if len(prompt) > 60 else prompt,
        })
    meta = {
        "sku_code": product["sku_code"],
        "product_name": product["name"],
        "subtitle": product.get("subtitle", ""),
        "shop_name": product.get("shop_name", "演示小铺"),
        "points": product.get("points", []),
        "tags": product.get("tags", ["AI 合成图"]),
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
