# cli.py · 入口（V1：仅去底白图）
# 用法：python -m manhua_studio --input 照片.jpg
import os
import argparse
from pathlib import Path

from .schemas import GenerationError
from .adapters import stage1_remove_bg


def main():
    parser = argparse.ArgumentParser(description="manhua V1：照片 → 白底商品图")
    parser.add_argument("--input", required=True, help="商品照片路径")
    args = parser.parse_args()

    uapi_key = os.getenv("UAPI_KEY")
    if not Path(args.input).exists():
        raise SystemExit(f"[错误] --input 照片不存在: {args.input}")
    if not uapi_key:
        raise SystemExit("[错误] 缺少 UAPI_KEY：S1 去底需要。\n       去 uapis.cn 免费申请并填入 .env。")

    print(f"[S1] UAPI 免费抠图去底白底: {args.input}")
    white = stage1_remove_bg(args.input, uapi_key)
    print(f"[完成] 白底图: {white}")


if __name__ == "__main__":
    main()
