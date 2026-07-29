# P10｜增强高斯过程：让物理先验进入主动学习

## 论文与资源

- 论文：[Physics makes the difference: Bayesian optimization and active learning via augmented Gaussian process](https://doi.org/10.1088/2632-2153/ac4baa)
- 期刊：Machine Learning: Science and Technology 3, 015003 (2022)
- 论文代码：[ziatdinovmax/AugmentedGaussianProcess](https://github.com/ziatdinovmax/AugmentedGaussianProcess)
- 后续通用实现：[ziatdinovmax/gpax](https://github.com/ziatdinovmax/gpax)
- 本仓库状态：`未开始`

## 这篇论文做了什么

普通 GP 常使用常数均值。增强/结构化 GP 将带有参数先验的物理模型放进均值函数，再由 GP 学习物理模型没有解释的残差：

```text
预测 = 物理模型给出的总体趋势 + GP 学到的残差
```

结构化 GP 输出完整预测分布，UCB 等采集函数再根据预测均值与不确定性选择下一点。因此它既能用于贝叶斯优化，也能用于主动学习，但它不是经典 PINN。

## 算法在闭环中的位置

| 模块 | 论文中的内容 |
|---|---|
| 先验知识 | 参数化物理模型与参数先验 |
| 代理模型 | 结构化/增强 GP |
| 不确定性 | GP 后验方差，同时考虑数据与物理参数 |
| 采集函数 | UCB 等 |
| Oracle | 测试函数、模拟或真实实验 |
| 目标 | 在小样本下提高外推和选样效率 |

## 公开资产与缺口

原始仓库提供论文 Notebook；GPax 提供结构化 GP、普通 GP、UCB、DKL、多保真模型、文档、Colab 和测试。

需要注意：

- 当前 GPax 已继续演化，不等于论文发表时的精确代码快照；
- 论文示例偏测试函数和物理格点模型；
- 物理均值函数错误时，先验也可能误导主动学习；
- 必须同时运行普通 GP 基线，不能只展示增强模型。

复现难度为**中等**。

## 忠实复现步骤

1. 固定原始仓库 commit 和 GPax 版本。
2. 在同一小数据集上拟合普通 GP，记录均值、方差和误差。
3. 编写只表达总体趋势的物理均值函数，并为参数设概率先验。
4. 拟合结构化 GP，检查物理参数后验是否合理。
5. 用相同初始点、预算和 UCB 参数分别运行两种 GP。
6. 比较 regret、样本效率、外推误差和不确定性校准。
7. 加入“错误物理先验”消融，检验方法是否稳健。

## 学习时必须回答

- 均值函数、核函数和观测噪声分别表达什么？
- 为什么加入物理趋势后，GP 仍需学习残差？
- 结构化 GP 与 PINN 的物理知识进入位置有什么不同？
- 哪些粘合剂知识足够可信，可以成为先验而不是普通输入特征？

## 对本项目的价值

价值非常高。它是“小样本 + 物理知识 + 主动学习”最直接的路线之一，通常比在缺少明确 PDE 时硬套 PINN 更现实。
