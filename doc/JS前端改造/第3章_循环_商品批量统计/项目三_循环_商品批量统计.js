// 项目三_循环_商品批量统计.js
// =====================================================================
// 第3章切片：循环 / 数组  →  商品批量统计（构件：aggregate）
//
// 设计约束（与「JS前端课程AI原生升级改造方案」一致）：
//   1. 零依赖：node 项目三_循环_商品批量统计.js 直接跑，不需要浏览器 / API / 联网。
//   2. 母体一致性：下面的 aggregate(products) 与期末综合案例「某某小店」
//      （项目七 renderProducts 数据驱动渲染汇合处）同名同签名。
//      注意：js-course 静态起步模板目前【还没有】 aggregate / products.js，
//      它由学生在项目三从零创建，并在项目七被 renderProducts 复用，零跳变。
//   3. 切片不碎：本文件 = 综合案例里的「构件·批量统计」那一步。
//   4. 数据契约：Product 字段与 Python 线 manhua_studio 对齐
//      (sku / name / price / selling_point / category / stock / images)。
// =====================================================================


// —— 示例商品（与 Python 线 manhua_studio / 期末综合案例的 Product 字段一致。
//    静态起步模板 starter 里暂无 products.js，本项目三由学生自己新建该数据文件。）——
const products = [
  { sku: "A001", name: "手作陶瓷杯", price: 39, selling_point: "粗陶质感·微波可用", category: "家居", stock: 12,
    images: ["images/p1.svg", "images/p2.svg", "images/p3.svg"] },
  { sku: "A002", name: "帆布托特包", price: 59, selling_point: "加厚帆布·通勤百搭", category: "箱包", stock: 8,
    images: ["images/p2.svg", "images/p1.svg", "images/p3.svg"] },
  { sku: "A003", name: "极简台灯", price: 89, selling_point: "护眼暖光·三档调光", category: "家居", stock: 5,
    images: ["images/p3.svg", "images/p1.svg", "images/p2.svg"] },
];


// =====================================================================
// 知识点预热：三种循环都能遍历数组，结果等价，只是写法不同
// =====================================================================
console.log("=== 知识点1：for 循环（带索引，最通用）===");
let sum1 = 0;
for (let i = 0; i < products.length; i++) {
  sum1 += products[i].stock;
}
console.log("for 循环算出的库存总量 =", sum1);

console.log("\n=== 知识点2：for...of（直接拿元素，最清爽）===");
let sum2 = 0;
for (const p of products) {
  sum2 += p.stock;
}
console.log("for...of 算出的库存总量 =", sum2);

console.log("\n=== 知识点3：while（满足条件才继续，注意别写成死循环）===");
let sum3 = 0, idx = 0;
while (idx < products.length) {
  sum3 += products[idx].stock;
  idx++;                       // 忘记自增就会死循环
}
console.log("while 算出的库存总量 =", sum3);


// =====================================================================
// 知识点4：分组统计 —— 用「对象当计数桶」，一个循环同时数出每个分类有几件
// =====================================================================
console.log("\n=== 知识点4：分组统计（对象当计数桶）===");
const cats = {};
for (const p of products) {
  cats[p.category] = (cats[p.category] || 0) + 1;   // 桶不存在先给 0，再 +1
}
console.log("各分类商品数 =", cats);   // { 家居: 2, 箱包: 1 }


// =====================================================================
// 母体函数：aggregate(products)
// ---------------------------------------------------------------------
// 学生任务：先把上面 4 个知识点串起来，自己写出 aggregate；
// 下面给出「参考实现」，与 js-course 模板首页、期末综合案例完全一致。
// 返回统计对象，方便后续渲染 / 接其它项目（项目四表单、项目七列表都复用它）。
// =====================================================================
function aggregate(list) {
  const result = {
    total: list.length,        // 商品种类
    stockSum: 0,               // 库存总量
    priceSum: 0,               // 价格合计（用于算均价）
    cats: {},                  // 各分类数量
    maxPrice: -Infinity,       // 最高价
    minPrice: Infinity,        // 最低价
    maxProduct: null,          // 最贵商品
    minProduct: null,          // 最便宜商品
  };
  for (const p of list) {
    result.stockSum += p.stock;
    result.priceSum += p.price;
    result.cats[p.category] = (result.cats[p.category] || 0) + 1;
    if (p.price > result.maxPrice) { result.maxPrice = p.price; result.maxProduct = p; }
    if (p.price < result.minPrice) { result.minPrice = p.price; result.minProduct = p; }
  }
  result.catCount = Object.keys(result.cats).length;
  result.avgPrice = result.total ? Math.round((result.priceSum / result.total) * 100) / 100 : 0;
  return result;
}


// ===================== 学生练习区（可直接运行） =====================

// 练习1：用 for 循环算「库存总量」（巩固索引遍历）
console.log("\n【练习1】库存总量：");
let s = 0;
for (let i = 0; i < products.length; i++) { s += products[i].stock; }
console.log("  =", s, "（应等于 25）");

// 练习2：用 for...of 数出「各分类商品数」（巩固分组统计）
console.log("\n【练习2】各分类商品数：");
const bucket = {};
for (const p of products) { bucket[p.category] = (bucket[p.category] || 0) + 1; }
console.log("  =", bucket);

// 练习3（课内）：用 for 循环找出「最贵 / 最便宜」商品
console.log("\n【练习3】最贵 / 最便宜：");
let hi = products[0], lo = products[0];
for (const p of products) {
  if (p.price > hi.price) hi = p;
  if (p.price < lo.price) lo = p;
}
console.log("  最贵：", hi.name, hi.price, "｜最便宜：", lo.name, lo.price);

// 练习4（课后）：把上面全部封装进 aggregate，返回统计对象
console.log("\n【练习4】调用 aggregate(products)：");
const stats = aggregate(products);
console.log("  ", stats);


// ===================== 一致性自检（可独立运行） =====================
// 针对固定的示例数据，断言 aggregate 的输出符合手算预期，
// 证明「切片写法」与模板首页 / 综合案例的 aggregate 行为一致。
// 学生换了自己的商品后，本段用「你自己的数据」重新断言，照常生效。
if (typeof require !== "undefined") {
  // node 环境：直接跑
  const expect = {
    total: 3,
    stockSum: 25,
    catCount: 2,
    maxPrice: 89,
    minPrice: 39,
    avgPrice: 62.33,
  };
  const got = aggregate(products);
  const ok =
    got.total === expect.total &&
    got.stockSum === expect.stockSum &&
    got.catCount === expect.catCount &&
    got.maxPrice === expect.maxPrice &&
    got.minPrice === expect.minPrice &&
    got.avgPrice === expect.avgPrice;
  console.log("\n" + (ok ? "✅ 自检通过：aggregate 统计结果与预期一致" : "❌ 自检失败：请检查循环 / 累加逻辑"));
}
