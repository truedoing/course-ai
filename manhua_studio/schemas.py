# schemas.py · 数据结构（V1 仅异常类；Product 在 V3 引入）
# 构件 7 · 统一异常：批量里个别失败可被捕获重试，不整批崩。
class GenerationError(Exception):
    pass
