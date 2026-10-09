# STORY.md · 第3章 循环·商品批量统计（教师版 PPT）

## ① 用户意图对齐
- **目标受众**：高职 JS 前端课教师，课堂投影使用，用于「项目三·循环」这一节的授课引导。
- **核心目标**：讲完学生能记住——① 循环遍历数组的三种写法；② 用「对象当计数桶」做分组统计；③ `aggregate(products)` 是贯穿全课、期末复用的母体函数。
- **PPT 长度**：8 页（封面 + 6 内容 + 收尾）。Hero 页 2 页（封面、收尾），占比 25%，符合 20–30%。
- **视觉调性**：学术严谨、蓝白克制、证据驱动（代码即证据）。
- **内容边界**：讲循环与 aggregate；不讲后续项目的 DOM/事件；不堆砌纯概念，每页都给可运行代码。

## ② 页面布局骨架
- 总页数：8 页，无独立目录/章节扉页（教学切片短 deck，直接内容流）。
- Hero 页：第 1 页（封面）、第 8 页（收尾/顺延预告）。两页之间间隔 ≥1 个 supporting 页。
- rhythm：P1 peak → P2–P7 valley/supporting → P8 transition/peak。
- 非对称版式占比：P2 左标题+右内容、P3 非对称双栏、P4 左大code+右文字、P5 左大code+右文字、P6 表格、P7 非对称双栏、P8 居中金句 → 非对称 ≥5/6 内容页（≥40% 达标）。
- 对称版式：仅 P6 表格页（1 页，≤2 达标）。

## ③ 页面大纲
| # | title | type | role | rhythm | layout | visual | anti_pattern |
|---|---|---|---|---|---|---|---|
| 1 | 第3章 循环·商品批量统计 | cover | hero | peak | 封面（深蓝顶条+中央标题） | L3 章节徽标 | 禁满版蓝金、禁装饰插画 |
| 2 | 教学目标与重难点 | content | supporting | valley | 左标题+右内容 | 无图，文字层次 | 禁等宽卡片横排 |
| 3 | 课堂时间现实：git 闭环优先 | content | supporting | valley | 非对称双栏（左提示/右对策） | 警示红药丸 | 禁大留白 |
| 4 | 三种循环遍历数组 | content | supporting | valley | 左大 code + 右要点 | CodeBlock(JS) L1 | 禁把代码塞进小角标 |
| 5 | 分组统计：对象当计数桶 | content | supporting | valley | 左大 code + 右要点 | CodeBlock(JS) L1 | 禁 50:50 等分双栏 |
| 6 | 母体函数 aggregate(products) | content | supporting | valley | 表格+洞察（签名/返回/复用） | 表 ≥70% | 禁纯文字无结构 |
| 7 | 验收三档 | content | supporting | valley | 非对称双栏（合格/良好/优秀） | 三档色块 | 禁深蓝实色卡多张 |
| 8 | 收尾与下节课预告 | ending | hero | transition | 居中金句+顺延说明 | 核心金句条 | 禁烟花/金装饰 |
