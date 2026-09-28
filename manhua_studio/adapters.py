# adapters.py · 外部服务适配层（V2：S1 去底 + S2 出图；S0 在 V4 加入）
import os, re, base64, mimetypes
from pathlib import Path
import requests

from .schemas import GenerationError
from .prompts import build_scene_prompt

UAPI_ENDPOINT = "https://uapis.cn/api/v1/image/matting"
SEEDREAM_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_MODEL = os.getenv("SEEDREAM_MODEL", "doubao-seedream-4-0-250828")


def _ensure_dir(p):
    p = Path(p)
    if not p.exists():
        p.mkdir(parents=True)


def _http_post_json(url, payload, headers, timeout=60):
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    return resp.status_code, resp.text


def _http_get_bytes(url, timeout=60):
    return requests.get(url, timeout=timeout).content


def _image_to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    b64 = base64.b64encode(Path(path).read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


# ---- S1 去底白底 ----
def _call_uapi_matting(image_path, api_key, timeout=120):
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    fields = {
        "image_base64": f"data:{mime};base64,{b64}",
        "image_name": Path(image_path).name,
        "output": "background",
        "background_color": "ffffff",
        "out_format": "png",
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.post(UAPI_ENDPOINT, files={k: (None, v) for k, v in fields.items()},
                         headers=headers, timeout=timeout)
    if resp.status_code != 200:
        raise GenerationError(f"UAPI HTTP {resp.status_code}: {resp.text[:200]}")
    obj = resp.json()
    b64_out = obj.get("image_base64")
    if not b64_out:
        raise GenerationError(f"UAPI 无返回图: {obj}")
    local = Path("assets/素材") / f"{Path(image_path).stem}_whitebg.png"
    _ensure_dir(local.parent)
    local.write_bytes(base64.b64decode(b64_out))
    return str(local)


def stage1_remove_bg(input_path, api_key):
    return _call_uapi_matting(input_path, api_key)


# ---- S2 场景化出图 ----
def _call_seedream_i2i(payload, api_key, timeout=150):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    status, body = _http_post_json(SEEDREAM_ENDPOINT, payload, headers, timeout)
    if status != 200:
        raise GenerationError(f"HTTP {status}: {body[:200]}")
    data = json.loads(body)
    item = (data.get("data") or [{}])[0]
    if item.get("url"):
        return item["url"]
    if item.get("b64_json"):
        return "b64:" + item["b64_json"]
    raise GenerationError("响应未含 url 或 b64_json")


def stage2_scene(white_path, name, selling_point, scene, api_key, prompt_override=None):
    """S2 场景化（Seedream 4.0 参考图生图）。返回本地场景图路径。"""
    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt_override or build_scene_prompt(name, selling_point, scene),
        "image": _image_to_data_uri(white_path),
        "size": "1024x1024",
        "response_format": "url",
        "watermark": False,
    }
    res = _call_seedream_i2i(payload, api_key)
    safe = re.sub(r"[^\w\u4e00-\u9fff]", "_", scene)
    local = Path("assets/素材") / f"{Path(white_path).stem}_scene_{safe}.png"
    _ensure_dir(local.parent)
    if res.startswith("b64:"):
        local.write_bytes(base64.b64decode(res[4:]))
    else:
        local.write_bytes(_http_get_bytes(res))
    return str(local)


def generate_image(task, api_key=None, white_path=None):
    """构件 4 · 真实出图（Seedream 4.0 参考图生图）。无 mock 分支——没有 key 由调用方报错。"""
    if not api_key:
        raise GenerationError("未配置 ARK_API_KEY（Seedream 4.0 场景化需要）")
    if not white_path:
        raise GenerationError("缺少去底白底图（S1 未执行）")
    out = stage2_scene(white_path, task["name"], task["selling_point"], task["angle"], api_key,
                       prompt_override=task.get("prompt"))
    return {"ok": True, "path": out, "metrics": None, "cost": "Seedream 4.0 免费额度"}
