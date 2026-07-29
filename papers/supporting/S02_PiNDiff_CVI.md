# S02｜PiNDiff-CVI：不完整物理、稀疏数据与不确定性

## 论文与资源

- 论文：[Probabilistic physics-integrated neural differentiable modeling for isothermal chemical vapor infiltration process](https://doi.org/10.1038/s41524-024-01307-5)
- 期刊：npj Computational Materials 10, 120 (2024)
- 作者仓库：[jx-wang-s-group/PiNDiff-CVI](https://github.com/jx-wang-s-group/PiNDiff-CVI)
- 本仓库状态：`未开始`

## 为什么收入本仓库

PiNDiff 保留已知 PDE 结构，同时用神经网络学习未知的扩散、反应和有效表面积算子，并通过深度集成给出不确定性。它适合“只知道部分机理、实验数据又很少”的材料过程问题。

论文**没有主动学习闭环**：它没有采集函数，也没有依据不确定性选择新实验再回填。它的预测分布可以在未来作为 UCB/EI 的输入，但这属于本项目后续扩展。

## 模型结构

| 模块 | 内容 |
|---|---|
| 输入 | 温度、压力、空间/时间状态和初始条件 |
| 已知物理 | CVI 过程的守恒与演化结构 |
| 学习模块 | 未知扩散、反应和有效表面积算子 |
| 不确定性 | 深度集成 |
| 输出 | 状态演化、孔隙率及未知物理量 |
| 原论文采集函数 | 无 |

## 复现资产与缺口

公开仓库包含 `environment.yml`、`main.py`、solver、YAML 配置、合成数据生成、实验数据和后处理 Notebook。

主要问题：

- README 较简略；
- 环境包含较旧且偏 Linux 的 JAX 依赖；
- 没有现成主动学习包装层；
- 迁移到其他材料过程时必须重新定义控制方程和未知算子。

复现难度为**中高**。

## 忠实复现步骤

1. 固定代码 commit，在隔离环境中按 `environment.yml` 安装。
2. 运行最小配置，并用 `gen_syn_data: True` 生成合成数据。
3. 训练 PiNDiff，复现未知算子和孔隙率预测。
4. 在未见温度/压力条件上检查预测误差。
5. 运行多个集成成员，核对不确定性是否随外推增大。
6. 保存论文图表对应结果和所有配置。
7. 后续扩展时，再把候选温度—压力池接入 UCB，而不改写论文原结论。

## 对本项目的价值

它比经典 PINN 更适合不完整机理，并提供了与主动学习连接所需的不确定性。但目前应作为物理代理模型支线，不列为主动学习核心复现。
