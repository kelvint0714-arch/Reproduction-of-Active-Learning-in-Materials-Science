# 材料主动学习文献持续检索

最后人工核验：**2026-07-29**

本文件是动态文献入口，不代表所有条目都已复现。论文只有同时通过“任务判定”和“来源核验”后，才进入正式论文卡。

## 准入规则

必须满足：

1. 研究对象是材料、化学、分子、原子模拟或材料实验；
2. 存在“训练 → 查询新标签 → 加入训练集 → 更新模型”的循环；
3. 查询目标主要是改善全局预测、类别边界、数据覆盖、相图或势能面；
4. DOI/出版社页面可以核验；
5. 代码、数据和复现性必须分别写明，找不到就明确写“未核验”，不得推断。

以下情况不能进入 `AL-core`：

- 只用 EI/UCB/EHVI 寻找最大、最小或 Pareto 最优；
- 只有一次监督训练和一次实验验证；
- 只有生成模型、PINN 或自动化平台，没有主动补标签；
- 标题写 Active Learning，但主要指标是 regret、最高性能或 top-k 优化。

## 已核验：真正的模型学习型 AL

| ID | 年份 | 论文 | AL 目标 | 公开资源 | 最小复现与优先级 |
|---|---:|---|---|---|---|
| A01 | 2024 | [Active learning for regression of structure–property mapping](https://doi.org/10.1039/D4DD00073K) | 用少量微结构标签学习结构—性质映射 | [NIST 页面](https://www.nist.gov/publications/active-learning-regression-structure-property-mapping-importance-sampling-and)、[代码/数据](https://github.com/usnistgov/active-learning) | 只跑 2D elastic 数据；**第一优先** |
| A02 | 2025 | [Density-aware active learning for materials discovery](https://doi.org/10.1039/D5CP02908B) | 用少量标签学习 MOF/COF 分离性质回归映射 | [代码](https://github.com/insane-group/Density_Aware_Greedy_Sampling)，Apache-2.0；合成数据可直接生成 | CPU 跑合成数据，比较 DAGS/iGS/QBC/RT/Random；**第一优先** |
| W01 | 2025 | [Data efficiency of classification strategies for chemical and materials design](https://doi.org/10.1039/D4DD00298A) | 用更少标签学好材料/化学分类边界 | [代码与数据](https://github.com/webbtheosim/classification-suite)、[分析](https://github.com/webbtheosim/classification-analysis) | 选 1–3 个任务做 RF/NN × Random/Uncertainty；高优先 |
| W02 | 2023 | [Exploiting redundancy in large materials datasets for efficient machine learning with less data](https://doi.org/10.1038/s41467-023-42992-y) | 构造更小但信息充分的材料训练集 | [代码](https://github.com/mathsphy/paper-data-redundancy)、[数据](https://zenodo.org/record/8200972) | 一个数据库×一个性质，比较 RF-U/XGB-U/QBC/Random；高优先 |
| A03 | 2025 | [A comprehensive benchmark of active learning strategies with AutoML for small-sample regression in materials science](https://doi.org/10.1038/s41598-025-24613-4) | 在 9 个小样本材料数据集上比较 17 种 AL 策略 | [代码与实验数据](https://github.com/bjhtud/Benchmark-AL-Mat) | 先选一个数据集和 3 种策略，缩短 AutoML 时间预算；中优先 |
| W03 | 2024 | [Active learning graph neural networks for partial charge prediction of metal-organic frameworks via dropout Monte Carlo](https://doi.org/10.1038/s41524-024-01277-8) | 用更少 DFT 标签学习 MOF 原子部分电荷 | [代码、模型和训练数据](https://github.com/tummfm/mof-al) | 先用预训练模型回放小数据；完整训练需处理旧 JAX 环境 |
| A05 | 2021 | [Entropy-based active learning of graph neural network surrogate models for materials properties](https://doi.org/10.1063/5.0065694) | 用熵采样减少 GNN 材料性质模型所需标签 | [代码](https://github.com/mdi-group/gp-net)、[数据和模型](https://doi.org/10.5281/zenodo.4922828) | 先复现随机与 entropy 学习曲线；中优先 |
| A06 | 2024 | [Informative Training Data for Efficient Property Prediction in Metal–Organic Frameworks by Active Learning](https://doi.org/10.1021/jacs.3c13687) | 用 RT-AL 构造 MOF 性质预测的代表性训练集 | [代码](https://github.com/AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs)、[数据/Notebook](https://doi.org/10.5281/zenodo.10511345) | 原数据较大，先下采样或只选一个性质 |
| A04 | 2024 | [Performance of uncertainty-based active learning for efficient approximation of black-box functions in materials science](https://doi.org/10.1038/s41598-024-76800-4) | 比较不确定性选样何时能改善全局函数逼近 | 论文使用多类公开材料数据；未核验到论文专用代码 | 先重实现论文最小基线；重要的负结果/边界论文 |
| A07 | 2023 | [Evaluating uncertainty-based active learning for accelerating the generalization of molecular property prediction](https://doi.org/10.1186/s13321-023-00753-5) | 改善分子性质模型的域外泛化 | [代码](https://github.com/pnnl/UQALE) | 比较 UQ 策略与 Random，重点检验改进是否稳定 |
| A08 | 2024 | [AIPHAD, an active learning web application for visual understanding of phase diagrams](https://doi.org/10.1038/s43246-024-00580-7) | 用不确定性采样学习完整相区和相边界 | [代码](https://github.com/NIMS-DA/aiphad)、[文档](https://nims-da.github.io/aiphad/docs/en/index.html) | 可安装应用并回放补充数据；相图路线第一优先 |
| W04 | 2024 | [Uncertainty-biased molecular dynamics for learning uniformly accurate interatomic potentials](https://doi.org/10.1038/s41524-024-01254-1) | 选择新原子构型，训练更均匀准确的势函数 | [代码](https://github.com/nec-research/alebrew)、[数据](https://doi.org/10.5281/zenodo.10776838) | Mac/CPU 只跑 alanine-dipeptide 小例子；中高难度 |
| W05 | 2020 | [On-the-fly active learning of interpretable Bayesian force fields for atomistic rare events](https://doi.org/10.1038/s41524-020-0283-z) | 超过不确定性阈值时才调用 DFT，扩充通用力场 | [FLARE](https://github.com/mir-group/flare)、[归档数据](https://doi.org/10.24435/materialscloud:2020.0017/v1) | 离线回放较可行；重新运行全部 DFT 难 |
| W06 | 2021 | [Autonomous materials synthesis via hierarchical active learning of nonequilibrium phase diagrams](https://doi.org/10.1126/sciadv.abg4930) | 内外两层 AL 学习非平衡相图 | [代码](https://github.com/gomes-lab/SARA_ScienceAdvances)、[原始数据](https://doi.org/10.7298/h63q-9r54) | 复现论文图可行；真实机器人闭环不可作为入门任务 |
| W07 | 2025/2026 | [FALCON: fast active learning for machine learning potentials](https://doi.org/10.1038/s41524-025-01897-8) | 用预测不确定性决定何时调用精确计算并重训势函数 | [代码](https://github.com/thequantumchemist/falcon)；论文给出最小 ASE 示例 | 先用 EMT 代替 DFT 跑最小 on-the-fly 示例 |

## 粘合剂直接相关：AL + BO 两阶段案例

| 年份 | 论文 | 正确分类 | 对本项目的价值 |
|---:|---|---|---|
| 2019 | [Prediction and optimization of epoxy adhesive strength from a small dataset through active learning](related/adhesive_hybrid/AD01_Epoxy_Adhesive_2019.md) | `author-labeled AL / Greedy exploitation + BO` | 前半段从 32 个实验出发，每轮选择预测强度最高的 5 个候选，不是 uncertainty AL；后半段使用 EI 做 BO。可指导粘合剂数据结构和未来应用验证，但不能替代通用 AL 基准。 |

## 2026 新论文观察区

这些论文很新，先收集，待代码/数据和任务边界进一步核验后再决定是否建立正式复现卡。

| 论文 | 初步判断 | 待核验 |
|---|---|---|
| [Training-free active learning framework in materials science with large language models](https://doi.org/10.1038/s41524-026-02136-4) | 在四个材料数据集上做少样本迭代推荐；结果偏“更快到达 top candidate”，可能靠近目标优化 | 正式排版版本、代码、完整数据、API/模型可替代性 |
| [Active learning enables generation of molecules that advance the known Pareto front](https://doi.org/10.1038/s41524-025-01924-8) | 生成模型＋量化模拟闭环；主结果是推进 Pareto 前沿，属于 AL/多目标优化混合 | 代码/数据入口和可运行许可证 |
| [Discovery Learning predicts battery cycle life from minimal experiments](https://doi.org/10.1038/s41586-025-09951-7) | AL＋物理引导＋零样本学习，目标是少量原型下预测新电池寿命 | 论文代码、工业数据开放范围、AL 消融 |
| [RAFFLE: active learning accelerated interface structure prediction](https://doi.org/10.1038/s41524-025-01749-5) | 主动扩充界面结构/能量数据，可能进入结构搜索与势函数旁支 | 官方代码入口、标签 Oracle、全局学习与低能结构优化的边界 |

## 明确分到 BO 或其他类别

| 论文/项目 | 归类理由 |
|---|---|
| PV-Lab Benchmarking | 明确比较材料贝叶斯优化，目标是更快找到全局最优 |
| NIST Fe-Co-Ni Benchmark | 作者使用广义 AL 术语，但任务、regret 和采集策略主体属于 BO |
| Bgolearn | 明确是单/多目标 Bayesian optimization 框架 |
| MolPAL | 主体是高通量分子候选池中的 top-k/高分子筛选，归入 molecular BO |
| Active learning for accelerated design of layered materials | 正文用 Expected Improvement 寻找目标性质，归入 BO |
| CAMD | 是自主 Agent/Experiment/Analyzer/Campaign 平台，不限定 AL 算法 |
| PINN / PiNDiff / DES ML | 是物理建模或普通监督学习，没有主动补标签闭环 |

## 复现优先级

```text
第一组：普通电脑、低门槛、概念最清楚
A01 NIST structure–property → A02 DAGS → W01 classification-suite

第二组：通用材料回归与不确定性
W02 data redundancy/QBC → A03 AutoML benchmark → A04 negative-result benchmark

第三组：结构模型与 GNN
A05 GP-Net → W03 MOF partial-charge GNN → P04 PBNN

第四组：相图、势函数和真实闭环
A08 AIPHAD → W04 ALEBREW / P09 DP-GEN → W05 FLARE → W06 SARA

应用迁移
通用 AL 基准 → 环氧粘合剂 AL 阶段 → 独立 BO 阶段
```

## 每次持续检索的固定步骤

1. 检索 `materials active learning regression uncertainty sampling`、`materials active learning code dataset`、`active learning interatomic potential`、`active learning phase diagram`；
2. 优先查看出版社、DOI、作者机构和官方代码仓库；
3. 先填“目标—指标—代码—数据—许可证—最小复现”，再决定分类；
4. 新论文先进入“观察区”，至少完成一次人工核验后才进正式清单；
5. 每次更新记录检索日期，不删除旧条目；分类变化必须写明理由；
6. 自动更新只能创建草稿 PR，不直接合并到 `main`。

## 更新日志

| 日期 | 变化 |
|---|---|
| 2026-07-29 | 首次严格区分 AL 与 BO；核验 15 篇模型学习型 AL、1 篇环氧 AL+BO 案例和 4 篇 2026 观察论文；将 PV-Lab 从 AL 主线移出。 |
