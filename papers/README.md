# 论文目录与复现优先级

“可复现性”是根据当前公开论文、代码、数据、环境说明和运行入口评估的，不代表本仓库已经成功跑完。

## 核心论文

| 编号 | 论文 | 主要算法位置 | 作者资源 | 当前可复现性 | 本项目用途 |
|---|---|---|---|---|---|
| P01 | [Liang et al., 2021](core/P01_PVLab_Benchmarking.md) | GP/RF 代理模型＋BO 采集函数 | 论文、5类材料数据、Notebook | 高，但旧依赖需修复 | 第一篇基础复现 |
| P02 | [Wang et al., 2022](core/P02_NIST_FeCoNi_Benchmark.md) | GP＋多种采集函数＋材料先验 | 论文、starter code、参考数据入口 | 中，代码与数据需重新接合 | 采集函数基准 |
| P03 | [Cao et al., 2026](core/P03_Bgolearn.md) | 多代理模型＋多采集函数 | PyPI、中文文档、CodeDemo | 高 | 现代工程框架 |
| P04 | [Allec & Ziatdinov, 2025](core/P04_PBNN_NeuroBayes.md) | PBNN/FBNN＋不确定性＋AL | 论文、NeuroBayes、Notebook | 高，计算量较大 | 神经网络主动学习 |
| P05 | [Narasimha et al., 2025](core/P05_DKL_on_STM.md) | DNN 表示＋GP＋UCB | 论文、数据、模拟 Notebook、仪器接口 | 中高；模拟可复现 | 混合模型主线 |
| P06 | [Graff et al., 2021](core/P06_MolPAL.md) | RF/FFN/MPNN＋批量 AL | 论文、代码、数据、publication tag | 高但依赖较重 | GNN与分子候选池 |

## 高级闭环与物理知识

| 编号 | 论文 | 主要内容 | 公开资源 | 当前可复现性 |
|---|---|---|---|---|
| P07 | [Kusne et al., 2020 — CAMEO](advanced/P07_CAMEO.md) | 相图/结构知识增强的闭环 AL | MATLAB/MEX代码、数据 | 中低，环境门槛较高 |
| P08 | [Montoya et al., 2020 — CAMD](advanced/P08_CAMD.md) | Agent–Experiment–Analyzer–Campaign | Python包、示例、数据 | 中，部分依赖较旧 |
| P09 | [Zhang et al., 2020 — DP-GEN](advanced/P09_DPGEN.md) | 多神经网络分歧选样＋MD/DFT | 成熟工程、教程、示例 | 工程上高，本地复现门槛很高 |
| P10 | [Ziatdinov et al., 2022 — Augmented GP](advanced/P10_Augmented_GP.md) | 物理概率模型＋GP＋BO/AL | 论文、Notebook、GPax实现 | 中高，原仓库示例较小 |

## 支持论文：不是材料主动学习主复现

| 编号 | 论文 | 为什么保留 | 是否主动学习 |
|---|---|---|---|
| S01 | [Amini Niaki et al., 2021](supporting/S01_Thermochemical_Curing_PINN.md) | 与树脂固化、传热和PINN最接近 | 否 |
| S02 | [Akhare et al., 2024](supporting/S02_PiNDiff_CVI.md) | 不完整物理＋稀疏数据＋概率建模 | 否，适合作为物理代理模块 |
| S03 | [Mu et al., 2024](supporting/S03_DES_ML.md) | XGBoost/ANN/CGAN/SHAP材料应用案例 | 否 |

## 选择逻辑

### 想理解随机森林怎样用于主动学习

先看 P01。RF负责预测，树间差异提供不确定性或排序依据，采集函数负责最终选样。

### 想理解神经网络怎样用于主动学习

先看 P04。普通神经网络不天然提供概率不确定性，PBNN将部分权重概率化，从而产生可用于采集函数的后验方差。

### 想理解传统模型与神经网络怎样结合

先看 P05。DKL让DNN负责高维表示，GP负责概率回归与不确定性，UCB负责下一测量点。

### 想理解 GNN 怎样筛选分子

先看 P06。MolPAL在同一分子候选池中比较RF、前馈网络和消息传递神经网络，并进行批量选样。

### 想理解物理知识怎样影响选样

依次看 P02、P07、P10。它们分别代表材料基准、真实闭环和概率先验三种层次。

### 想研究 PINN

先独立看 S01 和 S02。完成过程模型后，再研究怎样把过程预测或不确定性接入主动学习。不能把PINN残差配点选择当成材料候选选择。
