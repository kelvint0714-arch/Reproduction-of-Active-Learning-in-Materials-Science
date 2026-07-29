# P06｜MolPAL：分子候选池中的批量贝叶斯优化

## 论文与资源

- 论文：[Accelerating high-throughput virtual screening through molecular pool-based active learning](https://doi.org/10.1039/D0SC06805E)
- 期刊：Chemical Science 12, 7866–7881 (2021)
- 作者仓库：[coleygroup/molpal](https://github.com/coleygroup/molpal)
- 论文冻结版本：[publication release](https://github.com/coleygroup/molpal/releases/tag/publication)
- 本仓库状态：`未开始`

## 这篇论文做了什么

MolPAL 面向大规模分子候选池：先标注很少一部分分子，再让模型从剩余候选中选下一批，从而用远少于全库的昂贵评分查询找回高分子。

论文题名使用“pool-based active learning”，但正文明确将方法描述为 Bayesian optimization，评价目标也是 top-k 高分配体回收率，而不是整体预测误差。因此，本仓库将它归为**贝叶斯优化式分子筛选**；它可迁移为批量选样参考，但不作为材料主动学习核心论文。

论文同时比较传统模型和神经网络：

- 随机森林（RF）；
- 前馈神经网络（FFN）；
- 消息传递神经网络（MPNN，属于 GNN）；
- Greedy、UCB 等批量选择策略。

所以 GNN 在这里不是贝叶斯优化或主动筛选本身，而是用于分子表示和性质预测的代理模型。

## 贝叶斯优化式筛选映射

| 模块 | MolPAL 中的内容 |
|---|---|
| 候选池 | 带 SMILES 的大量分子 |
| 标签/Oracle | 预计算或昂贵的分子评分 |
| 表示 | 分子指纹或分子图 |
| 代理模型 | RF、FFN、MPNN |
| 不确定性 | RF 树间差异、FFN 的 MC dropout、MPN 的均值—方差估计等 |
| 采集策略 | Random、Greedy、UCB、TS、EI、PI 等批量策略 |
| 目标 | 以较小采样比例找回 top-k 高分候选 |
| 评价 | top-k recovery、采样比例、加速效果 |

## 公开资产与缺口

作者仓库包含代码、数据/教程入口、环境说明和论文对应版本信息，公开资产较完整。

主要门槛：

- 分子化学、PyTorch/图神经网络依赖较重；
- 论文讨论超大候选池，但本地首轮不应从亿级数据开始；
- 必须固定 publication tag/commit；
- 不同模型的不确定性实现需从代码核查；
- 评分函数在离线基准中不是湿实验。

当前可复现性为**高**，本地完整大规模实验的算力门槛较高。

## 忠实复现步骤

1. 固定论文 publication tag/commit 和小型公开数据。
2. 按作者文档运行最小候选池示例。
3. 先用 RF + Random/Greedy 跑通批量回填。
4. 再运行 UCB，并保存预测、方差和批次选择。
5. 在相同初始点、batch size 和预算下比较 RF、FFN、MPNN。
6. 画 top-k recovery—采样比例曲线，并运行多个种子。
7. 检查分子相似性泄漏和批内多样性。
8. 最后再讨论怎样迁移到有 SMILES 的聚合物、单体或固化剂候选。

## 学习时必须回答

- ECFP/分子指纹和 MPNN 学到的表示有何不同？
- 为什么超大候选池通常采用 batch 选择？
- Greedy 和 UCB 对 top-k recovery 的影响是什么？
- GNN 数据量不足时为什么可能不如 RF？
- 粘合剂配方由多组分和工艺共同决定时，单分子图是否足够？

## 对本项目的价值

P06 是 GNN 进入批量 BO 和自适应分子筛选的重要参考，也提供批量候选池实验协议。但它属于相关分子方法，不是材料主动学习核心论文；只有在候选具有可靠 SMILES/分子图时才能直接使用，纯表格配方应先以 GP/RF 为基线。
