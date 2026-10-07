# lesson4_prompt.py · 第4章切片：字符串 → 提示词构建（构件2）
# =====================================================================
# 设计约束（与「manhua章节切片映射方案」一致）：
#   1. 零依赖：不需要 API key、不需要联网、不需要 requests。
#   2. 母体一致性：下面的 build_scene_prompt / DEFAULT_SCENES 与
#      manhua_studio/prompts.py 逐字一致。综合阶段学生直接
#      `from manhua_studio.prompts import build_scene_prompt` 复用，零跳变。
#   3. 切片不碎：本文件 = 综合案例里的「构件2·提示词构建」那一步。
# =====================================================================

# —— 默认场景库（S2 展开单元：一张白底图 → 这几个场景各出一张）——
DEFAULT_SCENES = ["北欧客厅场景", "办公桌使用场景", "礼品盒包装场景"]


# —— 构件2 · 提示词模板：f-string 拼装商品名 + 卖点 + 场景 ——
# 学生任务：照着课堂讲的 f-string 写法，把这个函数体自己写出来。
# 下面给出「参考实现」，与母体 manhua_studio/prompts.py 完全一致。
def build_scene_prompt(name, selling_point, scene):
    """S2 场景化：把白底商品原样放入指定场景，商品须与白底图完全一致。"""
    return (f"将同一件商品原样放入以下场景，商品外观须与白底图完全一致、不可变形变色："
            f"场景={scene}；商品名={name}；卖点={selling_point}；"
            f"真实摄影质感，柔和自然光，主体突出，无文字、无水印、无其他无关物体")


# ===================== 学生练习区（可直接运行） =====================

# 练习1：给定一件商品，拼出一条给画图模型的提示词（纯字符串运算）
name = "青瓷茶漏"
selling_point = "过滤细腻，茶汤更清甜"
scene = "北欧客厅场景"

prompt = build_scene_prompt(name, selling_point, scene)
print("【练习1】单条提示词：")
print(prompt)
print()


# 练习2：循环 DEFAULT_SCENES，为一商品批量生成三张场景图提示词
# （巩固第2/3章学的 for 循环；本切片只新学「字符串怎么拼」）
print("【练习2】批量提示词（一商品 × 三场景）：")
for sc in DEFAULT_SCENES:
    print(" -", build_scene_prompt(name, selling_point, sc))
print()


# 练习3（课后）：把上面的循环封装成函数，返回提示词列表
def make_all_prompts(name, selling_point, scenes=DEFAULT_SCENES):
    """给定商品，按场景库批量生成提示词列表。"""
    return [build_scene_prompt(name, selling_point, sc) for sc in scenes]


print("【练习3】封装成函数，返回列表：")
for p in make_all_prompts("便携咖啡手冲壶", "一键萃取，出门也能喝到好咖啡"):
    print(" -", p)


# ===================== 一致性自检（可选） =====================
# 当你已 clone 并在 course-ai 根目录时，本段会把本文件的函数与
# 真实母体 manhua_studio.prompts 的输出做逐字比对，证明「调味一致」。
# 检测不到包时自动跳过，不影响上面教学运行。
if __name__ == "__main__":
    try:
        import sys, os
        root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        if root not in sys.path:
            sys.path.insert(0, root)
        from manhua_studio.prompts import (
            build_scene_prompt as _mother_fn,
            DEFAULT_SCENES as _mother_scenes,
        )
        assert _mother_fn(name, selling_point, scene) == build_scene_prompt(name, selling_point, scene), "提示词不一致！"
        assert _mother_scenes == DEFAULT_SCENES, "场景库不一致！"
        print("\n✅ 调味一致：本切片函数与 manhua_studio.prompts 输出完全相同")
    except ImportError:
        print("\n（未检测到 manhua_studio 包，跳过一致性自检；教学运行不受影响）")
