# P02｜NIST Fe-Co-Ni：材料主动学习策略基准

## 论文与资源

- 论文：[Benchmarking active learning strategies for materials optimization and discovery](https://doi.org/10.1093/oxfmat/itac006)
- 期刊：Oxford Open Materials Science 2, itac006 (2022)
- Starter code：[alex-aa-wang/Benchmarking-Active-Learning-Starter](https://github.com/alex-aa-wang/Benchmarking-Active-Learning-Starter)
- 公开数据：[NIST REMI](https://pages.nist.gov/remi/data/)
- 本仓库状态：`未开始`

## 这篇论文做了什么

论文在材料优化任务中系统比较探索、利用和多种贝叶斯采集策略，重点说明目标函数复杂度、数据稀疏程度和先验知识会改变“哪种策略最好”的答案。

公开 Fe-Co-Ni 数据可用于候选池回放，但 starter code 与完整数据和论文实验之间需要重新核对，不能仅运行两个脚本就声称复现整篇论文。

主要数据包含 921 个已测 Fe-Co-Ni 薄膜组成。三元组成满足总和约束，模型通常使用两个独立组成坐标；辅助信息还包括 XRD 结构或相区。论文对比了相对平滑的 Kerr rotation 与局部极值更多的磁矫顽力目标。

## 主动学习映射

| 模块 | 本论文中的内容 |
|---|---|
| 输入 | 921 个 Fe-Co-Ni 薄膜的组成坐标及相关结构信息 |
| 标签 | 候选的实验或构造目标值 |
| 代理模型 | 以 GP 为主 |
| 不确定性 | GP 后验方差 |
| 采集策略 | 纯探索、纯利用、UCB、Add-GP-UCB、Thompson Sampling、EI 等 |
| Oracle | Fe-Co-Ni 参考数据或论文定义的目标 |
| 目标 | 在有限查询中优化或发现目标区域 |
| 评价 | regret、命中速度及不同目标复杂度下的策略表现 |

## 它与 P01 的区别

P01 先帮助我们跑通材料 BO；P02 更集中地比较采集策略，并讨论材料知识如何改变选择。它提醒我们：不能脱离目标形状、噪声和先验，宣布某个采集函数永远最好。

当前可复现性为**中等**：

- 论文和 starter code 已公开；
- 代码体量很小；
- 完整数据入口、实验配置和论文图表之间仍需手工接合；
- 必须核对 REMI/数据来源与许可证。

## 忠实复现步骤

1. 固定论文版本、starter code commit 和 NIST REMI 数据版本。
2. 列出 starter code 中每个函数与论文方法的对应关系。
3. 固定同一候选池、初始点、预算、batch size 和随机种子。
4. 先运行 Random、纯探索和纯利用。
5. 再运行 UCB、Add-GP-UCB、TS 和 EI。
6. 保存每轮预测、方差、采集分数、选中点和 normalized minimum regret。
7. 在不同目标复杂度设置下重复，核对论文策略排序。
8. 明确哪些结果来自作者代码，哪些是我们的补全实现。

## 学习时必须回答

- 纯探索、纯利用和 UCB 的选点会怎样不同？
- Thompson Sampling 为什么不是简单地选最大方差？
- Add-GP-UCB 中加入的材料知识位于模型还是采集策略？
- 当目标函数很平滑或有多个局部极值时，策略排序为何变化？

## 对本项目的价值

这篇论文是采集函数基准主线。未来将 GP 换成 RF、PBNN 或 GNN 时，应尽量保持这里的候选池、预算与评价协议，才能判断提升来自模型还是选样策略。
