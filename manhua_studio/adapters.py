# adapters.py · 外部服务适配层（V1 仅 S1 去底；S0/S2 在后续版本加入）
# 这一层只跟"外面的世界"打交道：HTTP 请求、UAPI 免费抠图。
import os, base64, mimetypes
from pathlib import Path
import requests

from .schemas import GenerationError

UAPI_ENDPOINT = "https://uapis.cn/api/v1/image/matting"


def _ensure_dir(p):
    p = Path(p)
    if not p.exists():
        p.mkdir(parents=True)


def _call_uapi_matting(image_path, api_key, timeout=120):
    """S1 去底白底（UAPI 免费抠图）。本地照片 → 上传 → 返回白底图。"""
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
    """S1 去底白底（UAPI 免费抠图）。返回本地白底图路径。"""
    return _call_uapi_matting(input_path, api_key)
