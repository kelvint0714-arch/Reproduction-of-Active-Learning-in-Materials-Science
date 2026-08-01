# PS01｜聚合物太阳能电池 NLP 数据与顺序选样复现

**路径状态**：`source-lock-needed`
**论文**：[Accelerating Materials Discovery for Polymer Solar Cells: Data-Driven Insights Enabled by Natural Language Processing](https://doi.org/10.1021/acs.chemmater.4c00709)
**正式论文卡**：[`papers/related/goal_directed_al_bo/PS01_Polymer_Solar_Cells_2024.md`](../../../papers/related/goal_directed_al_bo/PS01_Polymer_Solar_Cells_2024.md)

## 定位与边界

论文先以 NLP 建立聚合物太阳能电池历史数据，再预测 PCE，并用 GPR-UCB/PI/EI/TS、Greedy、contextual bandit 与 Random 模拟怎样更快找到高 PCE 供体—受体组合。这是**目标导向 AL / BO / bandit 混合应用**，不是多目标 AL。

- 最小复现：官方 curated data 上运行 PCE 监督模型，以及 Random/Greedy/GP-EI 小预算回放。
- 忠实复现：按作者命令运行 PCE、顺序选样和 NLP 评价，核对论文图表及历史时间回放。
- CPU 普通电脑可运行；作者提示并行 contextual bandit 最好 ≥8 cores。
- 回顾性历史模拟不等于真实自动实验，也受发表偏差和跨论文条件差异影响。

## 来源锁定

一手来源：

- ACS 正式论文 DOI：`10.1021/acs.chemmater.4c00709`
- 作者代码与数据：[pranav-s/PolymerSolarCellsML](https://github.com/pranav-s/PolymerSolarCellsML)，MIT
- 官方数据：`dataset/polymer_solar_cell_curated_data.xlsx`、`polymer_solar_cell_extracted_data.csv` 和 `metadata/fp_dict.pkl`
- 上游无 tag/release，必须解析 `main` SHA。

```bash
git clone https://github.com/pranav-s/PolymerSolarCellsML.git \
  ../upstream/PS01-polymer-solar-cells
git -C ../upstream/PS01-polymer-solar-cells remote -v
git -C ../upstream/PS01-polymer-solar-cells branch --show-current
git -C ../upstream/PS01-polymer-solar-cells describe --tags --always --dirty
git -C ../upstream/PS01-polymer-solar-cells rev-parse HEAD
git -C ../upstream/PS01-polymer-solar-cells status --short
shasum -a 256 ../upstream/PS01-polymer-solar-cells/LICENSE \
  ../upstream/PS01-polymer-solar-cells/environment.yml
find ../upstream/PS01-polymer-solar-cells/dataset \
     ../upstream/PS01-polymer-solar-cells/metadata \
  -type f -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/PS01/data_sha256.txt
```

Pickle 是不可信可执行载荷：只在锁定作者 commit、隔离环境中读取，不接受外部替换。写入 `reproduction/runs/PS01/source_lock.md`。

## 环境

环境名采用作者文件的 `psc`。官方 `environment.yml` 已明确 Python 3.10、RDKit 2023.9.4、scikit-learn 1.3.2，并给出完整 Linux 锁。

```bash
conda env create -f ../upstream/PS01-polymer-solar-cells/environment.yml
conda activate psc
python -m pip install -e ../upstream/PS01-polymer-solar-cells
python -m pip check
python -m pip freeze > reproduction/runs/PS01/pip-freeze.txt
conda env export --no-builds > reproduction/runs/PS01/environment.yml
```

Apple Silicon 不能原样解析 Linux build 时，使用 Linux x86_64 容器；重建跨平台环境必须保留版本并写 `deviations.md`。

## T0｜来源、数据与时间协议核验

1. 固定 commit、许可、环境和数据哈希。
2. 审计 curated/extracted 数据的行数、单位、缺失、重复论文、供体/受体名称标准化、PCE 聚合规则。
3. 检查 `fp_dict.pkl` 的键与归一化名称一一对应，记录无法匹配和结构重复。
4. 从 `sequential_selection/parse_args.py` 导出所有默认值、种子、初始集、目标方向、停止和时间回放规则。
5. 建立论文图表与 `PCE_models.py`、`PSC_iterative_selection.py`、`nlp_eval.py` 输出的映射。

## T1｜最小 smoke test

```bash
cd ../upstream/PS01-polymer-solar-cells
python ./PolymerSolarCellsML/property_prediction/PCE_models.py --use_median
python ./PolymerSolarCellsML/nlp_eval.py
```

顺序选样先复制作者配置并缩小种子/预算；不使用 `--run_parallel_paths`：

```bash
python ./PolymerSolarCellsML/sequential_selection/PSC_iterative_selection.py
```

若默认即论文全量，应通过 `parse_args.py` 的公开参数缩小，而不是改源码。Smoke 成功要求：数据/指纹对齐、至少一条 Random 和 GP/Greedy 轨迹完成、目标为最大化 PCE、候选不重复。

## T2｜忠实复现论文主结果

1. 按作者 README 原命令运行 `PCE_models.py --use_median`。
2. 使用 `PSC_iterative_selection.py --run_parallel_paths` 运行全部作者策略和种子。
3. 保留论文的年份/历史可用性规则，逐轮只能使用当时已发表/已观测数据。
4. 运行 `nlp_eval.py`，核对 2-/3-/4-tuple precision、recall、F1。
5. 对 GPR-UCB/PI/EI/TS、Greedy、linear contextual bandit 和 Random 保存每轮 donor/acceptor、PCE、预测/采集值。
6. 重画论文的 PCE 预测、研究历史与顺序选择图；逐项比较作者统计。

## T3｜统一协议与消融

- 随机划分、按年份回放和 donor/acceptor 结构分组三种协议分开报告。
- 比较 Random、Greedy、GP-EI、GP-UCB 与 contextual bandit，固定同一初始对、预算和种子。
- 消融结构指纹、工艺条件、名称聚合与 median/单条测量标签。
- 评估发表偏差：按期刊/年份/实验条件分层，检查高 PCE 过度代表。
- 报告 best-so-far、top-1% 查询数、regret AUC，同时报告固定测试 MAE/RMSE。

## T4｜迁移到 DGEBA/粘合剂数据

把 donor＋acceptor＋器件条件的适配器迁移为“树脂＋固化剂＋离子液体＋多酚＋配比/固化条件”。每个组分有稳定结构 ID/指纹，工艺条件单独编码；候选对/配方 ID 不随清洗改变。

先在 Synthetic 表离线回放 Random/Greedy/GP-EI，明确只验证代码。真实数据按实验日期回放并按结构家族分组；禁止让后续实验或同义结构提前进入指纹/聚合。它可以指导组合材料数据结构，但不能证明粘合剂 PCE 模型可直接迁移。

## 公平性与评价

- 优化主指标：best-so-far PCE、simple regret、达到 top 1% 的查询数、成功率和 regret AUC。
- 监督辅助指标：MAE/RMSE/\(R^2\)，按年份和结构分组报告。
- NLP：precision、recall、F1，按 tuple 层级与误差类型报告。
- Random 是必需基线；所有策略共享初始候选、预算、batch 和种子。
- 未来年份、同一论文重复器件、同义 donor/acceptor 和结构指纹均可能泄漏。
- PCE 测量条件差异与发表偏差不能被模型性能掩盖。

## 证据交付

```text
reproduction/runs/PS01/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── data_sha256.txt
├── data_audit.md
├── time_replay_protocol.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

原始作者数据保持只读；所有名称清洗、去重和时间过滤都保存可追踪映射。

## 停止条件

- Smoke 成功：监督脚本/NLP 评价可运行，至少一条顺序轨迹完成且无候选重复或未来标签泄漏。
- 立即阻塞：pickle/数据哈希异常、名称—指纹错位、年份规则无法重建、环境修复改变模型行为。
- 只有监督、NLP、全部顺序策略/种子、时间回放、论文图表核对、环境和偏差齐全才可标 `completed`。
