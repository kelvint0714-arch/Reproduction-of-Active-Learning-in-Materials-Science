# 论文目录与复现优先级

本目录按论文的**实际目标**分类，不按标题中是否出现 “active learning” 分类。

- `Axx`：这次严格筛选后新增的模型学习型主动学习论文；
- `Pxx`：仓库原有论文卡，已按 AL、BO、平台等重新归档；
- `Sxx`：物理建模或普通监督学习支持论文。

“可复现性”只表示当前公开论文、代码、数据和运行入口的完备程度，不代表本仓库已经跑通。

## 主动学习：优先复现论文

| 编号 | 论文卡 | 任务 | 代码/数据 | 建议 |
|---|---|---|---|---|
| A01 | [NIST 微结构—性质映射](active_learning/literature/A01_NIST_Structure_Property_AL_2024.md) | 回归；全局模型学习 | 代码和预计算数据公开 | **第一组，普通电脑** |
| A02 | [DAGS 密度感知 AL](active_learning/literature/A02_DAGS_Density_Aware_AL_2025.md) | MOF/COF 回归；代表性选样 | 代码公开，合成数据可直接生成 | **第一组，普通电脑** |
| A03 | [Benchmark-AL-Mat](active_learning/literature/A03_Benchmark_AL_Mat_2025.md) | 9 个小样本材料回归基准 | 代码/结果公开；完整数据按论文来源取得 | 缩小 AutoML 预算后做 |
| A04 | [材料黑箱函数逼近](active_learning/literature/A04_Koizumi_BlackBox_Approximation_2024.md) | 检验 uncertainty AL 何时失效 | 算法依赖公开，论文专用数据/脚本不完整 | 重要方法边界，非首个忠实复现 |
| A05 | [GNN 表征＋GP 熵采样](active_learning/literature/A05_Entropy_GNN_Surrogate_2021.md) | 晶体形成能全局预测 | 代码和 Zenodo 实验包公开 | 旧 TF/MEGNet 环境，先回放 embedding |
| A06 | [MOF RT-AL](active_learning/literature/A06_MOF_RT_AL_2024.md) | 用代表性小训练集预测 MOF 性质 | 代码和 4.1 GB 数据公开 | 只选一个目标和描述符 |
| A07 | [UQALE 分子 OOD 泛化](active_learning/literature/A07_UQALE_Molecular_Generalization_2023.md) | 用不确定性补足训练域 | 代码和数据入口公开 | 先做一个性质、一次批量选样 |
| A08 | [AIPHAD 相图 AL](active_learning/literature/A08_AIPHAD_Phase_Diagram_2024.md) | 学习相区和相边界 | Python 包、代码和补充数据公开 | 相图路线首选 |

持续检索结果、2026 观察论文和准入规则见 [LITERATURE_WATCH](LITERATURE_WATCH.md)。

## 主动学习：原有论文与高级闭环

| 编号 | 论文卡 | 分类 | 复现定位 |
|---|---|---|---|
| P04 | [PBNN / NeuroBayes](active_learning/core/P04_PBNN_NeuroBayes.md) | `AL-core` | 神经网络不确定性与模型学习 |
| P05 | [DKL-on-STM](active_learning/closed_loop/P05_DKL_on_STM.md) | `AL+BO hybrid` | 图像表示＋GP＋仪器闭环 |
| P07 | [CAMEO](active_learning/closed_loop/P07_CAMEO.md) | `AL+BO hybrid` | 相图知识与真实实验闭环 |
| P09 | [DP-GEN](active_learning/concurrent_learning/P09_DPGEN.md) | `AL-concurrent` | 多模型分歧、MD/DFT 与势函数数据覆盖 |

## 贝叶斯优化：独立副线

| 编号 | 论文卡 | 为什么不是 AL 核心 | 用途 |
|---|---|---|---|
| P01 | [PV-Lab Benchmarking](bayesian_optimization/benchmarks/P01_PVLab_Benchmarking.md) | 目标是更快找到材料全局最优，主要报告发现/优化指标 | 学习 GP/RF 与 BO 基准 |
| P02 | [NIST Fe-Co-Ni Benchmark](bayesian_optimization/benchmarks/P02_NIST_FeCoNi_Benchmark.md) | 作者用广义 AL 术语，但实质比较 BO schemes 和 regret | 学习采集函数与材料先验 |
| P03 | [Bgolearn](bayesian_optimization/frameworks/P03_Bgolearn.md) | 明确是单/多目标 BO 框架 | 现代工程工具 |
| P10 | [Augmented GP](bayesian_optimization/physics_informed/P10_Augmented_GP.md) | 同时讨论 BO/AL，但论文案例主体偏结构化 GP-BO | 学习物理先验怎样进入概率模型 |

## 相关但不作为 AL 核心

| 编号 | 论文卡 | 分类 | 保留理由 |
|---|---|---|---|
| P06 | [MolPAL](related/molecular_bo/P06_MolPAL.md) | 分子池批量 BO / top-k 筛选 | 学习 RF、FFN、MPNN 和大候选池工程 |
| P08 | [CAMD](related/closed_loop_platforms/P08_CAMD.md) | 自主闭环平台 | 学习 Agent–Experiment–Analyzer–Campaign 架构 |
| AD01 | [环氧粘合剂小数据闭环](related/adhesive_hybrid/AD01_Epoxy_Adhesive_2019.md) | 作者称 AL 的 Greedy exploitation＋后续 BO | 粘合剂数据结构和两阶段迁移案例 |
| PS01 | [聚合物太阳能电池](related/goal_directed_al_bo/PS01_Polymer_Solar_Cells_2024.md) | NLP 数据＋目标导向 AL/BO/bandit | 组合材料数据与顺序选样，高价值应用复现 |
| H01 | [锂盐连续结晶 HITL](related/goal_directed_al_bo/H01_Lithium_Crystallization_HITL_2025.md) | 人在回路 AL＋多目标过程优化 | 学习专家审核和真实实验闭环 |
| L01 | [LLM-AL](related/goal_directed_al_bo/L01_LLM_AL_2026.md) | LLM 驱动的离散池目标优化 | 前沿高级案例，完整复现依赖商业 API |

## 支持论文

| 编号 | 论文卡 | 为什么保留 | 是否主动学习 |
|---|---|---|---|
| S01 | [固化过程 PINN](supporting/physics_modeling/S01_Thermochemical_Curing_PINN.md) | 与树脂固化、传热和 PINN 接近 | 否 |
| S02 | [PiNDiff-CVI](supporting/physics_modeling/S02_PiNDiff_CVI.md) | 不完整物理＋稀疏数据＋概率建模 | 否 |
| S03 | [DES ML](supporting/general_ml/S03_DES_ML.md) | XGBoost/ANN/CGAN/SHAP 材料应用案例 | 否 |

## 怎样选下一篇

### 现在第一次真正复现主动学习

先做 A01 或 A02。两者都以固定测试集误差和标签效率为主要指标，不会把“找到最高性能”误当成“学好模型”。

### 想理解随机森林、XGBoost 怎样进入 AL

先做 A02，再看 `LITERATURE_WATCH` 中的材料数据冗余/QBC 论文。树模型负责预测和不确定性/committee 分歧，查询策略负责选新标签。

### 想理解神经网络或 GNN

顺序建议：

```text
A05：GNN embedding + GP
→ P04：部分贝叶斯神经网络
→ W03：MOF partial-charge GNN + MC Dropout
→ P09：多神经网络分歧 + MD/DFT
```

### 想理解相图和真实实验

先做 A08 的离线相图回放，再阅读 P07。软件回放与真实合成/表征必须分开评价。

### 想寻找最高性能材料

转到 BO 副线，从 P01 开始。不要用 BO 的 regret 或 best-so-far 证明主动学习的全局模型已经准确。

应用顺序建议为 `PS01 → H01 → L01`：先复现公开聚合物数据上的传统 GP/bandit，再理解真实 HITL 闭环，最后评估依赖外部 LLM API 的高级方法。

### 想研究 PINN

独立看 S01 和 S02。只有可信方程、边界条件和参数定义齐全时才使用 PINN；PINN 残差配点选择不等于选择下一种材料做实验。
