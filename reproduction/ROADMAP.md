# 论文复现路线

路线按“基础材料 BO → 采集函数 → 神经网络不确定性 → DKL/GNN → 物理先验 → 真实闭环”推进。

## R1：PV-Lab 材料 BO 基准

目标：

- 先在一个仓库自带的真实材料数据集上跑通候选池闭环；
- 比较 GP-ARD、普通 GP 和 RF；
- 比较 Random、Greedy、EI、PI、LCB/UCB；
- 理解 batch size、初始样本和随机种子怎样影响结果。

完成标准：

- 至少一个数据集成功运行；
- 作者结果趋势能够重现；
- 运行 30 个以上随机种子；
- 输出 best-so-far、regret 和 top-k 命中曲线；
- 写出原始代码需要修复的依赖或兼容性问题。

## R2：NIST Fe-Co-Ni 主动学习基准

目标：

- 比较纯探索、纯利用、UCB、Add-GP-UCB、Thompson Sampling 和 EI；
- 理解材料相图或结构先验如何进入采集过程；
- 区分普通 BO 与科学/物理知识增强 AL。

完成标准：

- 固定同一个 Fe-Co-Ni 候选池和初始点；
- 重复多次并报告最小 regret；
- 核对论文中不同目标复杂度下的策略差异；
- 明确 starter code 与数据之间的缺口。

## R3：Bgolearn

目标：

- 使用现代材料 BO 框架复现单目标回归示例；
- 了解 GP、SVM、RF、AdaBoost、MLP 怎样作为可替换代理模型；
- 比较 EI、AEI、EQI、REI、UCB、PoI、PES 和 KG 中与当前任务相关的方法。

完成标准：

- 运行官方 CodeDemo；
- 保存版本和环境；
- 用同一 CSV 分别调用两种代理模型和三种采集函数；
- 输出下一批候选及推荐依据；
- 不把“成功调用软件”当作自己的算法贡献。

## R4：PBNN / NeuroBayes

目标：

- 复现部分贝叶斯神经网络的预测均值与方差；
- 比较 GP、普通神经网络、全贝叶斯 NN 和部分贝叶斯 NN；
- 测试理论/模拟预训练如何帮助小样本实验主动学习。

完成标准：

- 跑通官方 PBNN 主动学习示例；
- 检查不确定性与真实误差是否相关；
- 比较相同预算下的发现效果；
- 记录贝叶斯层数量、采样步数和计算时间。

## R5：DKL-on-STM / GPax

目标：

- 理解 DNN 如何学习高维结构表示；
- 理解 GP 如何在 embedding 上给出均值与不确定性；
- 复现 UCB 驱动的逐点实验选择。

完成标准：

- 先运行作者提供的模拟工作流，不连接真实仪器；
- 复现 DKL 输入、scalar target、GP 预测和下一坐标选择；
- 对比普通 GP 与 DKL；
- 尝试将图像输入替换成普通材料描述符，确认接口可迁移。

## R6：MolPAL

目标：

- 复现分子候选池的批量主动学习；
- 比较 RF、前馈网络和消息传递神经网络；
- 观察 Greedy 与 UCB 在不同 batch size 下的差异。

完成标准：

- 使用仓库自带的小型数据和 publication tag；
- 不从 1 亿规模库开始；
- 报告 top-k recovery 与采样比例；
- 明确分子图/GNN只在拥有可靠结构表示时使用。

## R7：物理与闭环高级工作

### CAMEO

学习结构/相图知识如何改变采集决策。原代码为 MATLAB，优先理解和小规模重实现，不作为第一份 Python 复现。

### CAMD

学习 Agent、Experiment、Analyzer、Campaign 的模块化闭环。旧依赖可能需要隔离环境，不直接混入主环境。

### DP-GEN

学习多神经网络分歧如何选择需要 DFT 标注的新结构。该路线依赖 MD、DFT 和通常的 HPC 环境，只作为高级独立环境。

## R8：PINN 与材料过程

先独立复现热传导/固化动力学或 PiNDiff，再研究它怎样向主动学习提供：

- 过程预测；
- 隐状态或物理参数；
- 物理先验；
- 多保真标签；
- 不确定性。

没有可信方程时，不将普通神经网络称为 PINN。

## 最终统一实验

候选的统一比较矩阵：

| 表示/代理模型 | 不确定性 | 采集函数 |
|---|---|---|
| GP | GP posterior | Random / UCB / EI |
| RF | 树间方差 | Random / UCB / Uncertainty |
| XGBoost ensemble | 模型间分歧 | Random / UCB / EI |
| PBNN | 后验方差 | Random / UCB / EI |
| GNN ensemble | 模型间分歧 | Random / UCB / EI |
| DNN/GNN + GP | GP posterior | Random / UCB / EI |
| 物理先验模型 | 概率后验或集成 | Random / UCB / EI |

所有方法必须使用相同数据、初始点、预算、batch size 和随机种子集合。
