# schemas.py · 数据结构（V3 引入 Product/Character；V1 仅 GenerationError）
class GenerationError(Exception):
    pass


class Product:
    def __init__(self, name, material, ref_image, seed):
        self._name = name
        self.material = material
        self.ref_image = ref_image
        self.seed = seed

    def score(self, metrics):
        """电商图一致性打分（0-1）。全部来自可判定指标，无形容词。"""
        base = (0.40 * metrics["bg_purity"]
                + 0.30 * metrics["comp_ratio"]
                + 0.30 * metrics["clarity"])
        if metrics["text_ratio"] > 0.20:
            base -= 0.5 * (metrics["text_ratio"] - 0.20)   # 文字超平台上限扣分
        return round(max(0.0, min(1.0, base)), 2)


class Character(Product):
    """继承示例：漫剧角色是 Product 的一个实例，重写 score 更严（人脸必须完整）。"""
    def score(self, metrics):
        if not metrics.get("face_ok"):
            return 0.2
        base = (0.20 * metrics["bg_purity"]
                + 0.50 * metrics["comp_ratio"]
                + 0.30 * metrics["clarity"])
        return round(max(0.0, min(1.0, base)), 2)
