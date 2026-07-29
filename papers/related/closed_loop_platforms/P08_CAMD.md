# P08｜CAMD：自主材料发现闭环的软件架构

## 论文与资源

- 论文：[Autonomous intelligent agents for accelerated materials discovery](https://doi.org/10.1039/D0SC01101K)
- 期刊：Chemical Science 11, 8517–8532 (2020)
- 作者仓库：[TRI-AMDD/CAMD](https://github.com/TRI-AMDD/CAMD)
- 本仓库状态：`未开始`

## 这篇论文做了什么

CAMD 将材料发现流程拆成四个角色：

```text
Agent 选择候选
  → Experiment 返回计算或实验结果
  → Analyzer 评估结果与进度
  → Campaign 管理循环、状态和停止条件
```

它支持先在已有数据库上做 `after-the-fact` 离线模拟，再连接 DFT 或真实实验。

CAMD 可以承载主动学习，但它首先是一个**闭环软件框架**。只有当 Agent 使用代理模型、不确定性或探索—利用策略时，该循环才是我们关注的主动学习；启发式 Agent 不应自动称为主动学习。

## 算法在闭环中的位置

| 模块 | CAMD 中的对应物 |
|---|---|
| 候选池 | 可计算或可实验的材料集合 |
| 代理模型/策略 | `Agent` |
| Oracle | `Experiment`，可以是历史数据库、DFT 或真实实验 |
| 结果分析 | `Analyzer` |
| 循环与状态 | `Campaign` |

随机森林、GP 或神经网络可放进 Agent；CAMD 本身不规定唯一模型。

## 公开资产与缺口

公开资产包括 Python 包、示例、Binder、OQMD 相关特征、requirements、回溯式实验接口和 Apache-2.0 许可证。

主要缺口：

- 部分依赖和安装说明较旧；
- 完整论文流程涉及 OQMD、VASP 和 AWS Batch；
- 真实 DFT 闭环需要额外软件、许可证和算力；
- 成功运行框架不等同于复现论文中的发现效率。

离线回放难度为**中高**，论文级 DFT 闭环难度为**很高**。

## 忠实复现步骤

1. 固定论文对应代码版本，在独立环境中安装 CAMD。
2. 运行最小示例，记录依赖修复，不先连接 VASP。
3. 准备 OQMD 候选和种子数据，运行 `after-the-fact` Experiment。
4. 先复现随机 Agent，作为最低基线。
5. 再运行带不确定性或探索—利用的 Agent。
6. 在相同初始点、预算和随机种子下比较发现率。
7. 最后才尝试把候选表替换成聚合物或粘合剂数据。

## 学习时必须回答

- Agent、模型和采集函数是不是同一个东西？
- 为什么 Experiment 可以先用数据库查询代替？
- Campaign 需要保存哪些状态，才能中断后继续？
- 把新材料体系接入 CAMD 时，哪些模块可复用，哪些必须重写？

## 对本项目的价值

价值高，但偏工程架构。它提供“如何把模型、选样、实验和分析装进可持续运行的闭环”的参考，而不是主动学习核心算法，因此应作为相关平台论文管理。
