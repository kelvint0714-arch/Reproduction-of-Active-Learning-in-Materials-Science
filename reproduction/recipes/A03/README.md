# A03｜Benchmark-AL-Mat 小样本材料回归基准复现路径

> 状态：`source-lock-needed`；忠实 AutoML 主结果目前有明确代码缺口，本文不声称已运行。

## 定位与边界

- 论文：*A comprehensive benchmark of active learning strategies with AutoML for small-sample regression in materials science*，DOI：[10.1038/s41598-025-24613-4](https://doi.org/10.1038/s41598-025-24613-4)。
- 分类：AL 基准，不是 BO。论文口径是 17 种 AL＋Random、9 个数据集、Auto-sklearn 代理。
- 最小复现：仓库自带 UCI Concrete，跑 RandomSearch、TreeBasedRegressor_Representativity、RD_GS_ALR。
- 关键边界：当前作者仓库只打包 UCI Concrete，`requirements.txt` 没有 Auto-sklearn，当前 `active_learning()` 主要保存查询索引而未计算论文所述 AutoML 学习曲线。T1 可核验采样管线；T2 在找回/重实现缺失的 AutoML 评估层前不能称忠实复现。
- 门槛：T1 CPU；完整 9 数据集×18 策略×20 种子×逐轮 AutoML 是 HPC 级任务。

## 来源锁定

- 作者代码：[bjhtud/Benchmark-AL-Mat](https://github.com/bjhtud/Benchmark-AL-Mat)。
- 论文正文 Table 2 是九个数据源的权威入口；不得把仓库单个示例数据误写成完整数据包。

```bash
git clone https://github.com/bjhtud/Benchmark-AL-Mat.git ../upstream/A03-benchmark-al-mat
git -C ../upstream/A03-benchmark-al-mat remote -v
git -C ../upstream/A03-benchmark-al-mat branch --show-current
git -C ../upstream/A03-benchmark-al-mat describe --tags --always --dirty
git -C ../upstream/A03-benchmark-al-mat rev-parse HEAD
git -C ../upstream/A03-benchmark-al-mat status --short
shasum -a 256 ../upstream/A03-benchmark-al-mat/dataset/meta.csv \
  ../upstream/A03-benchmark-al-mat/dataset/uci-concrete/concrete_data.csv
```

把 SHA、许可证（MIT）、论文版本、九个数据的 URL/许可证/哈希分别记录在
`reproduction/runs/A03/source_lock.md`。

## 环境

- 环境名：`repro-A03`。
- 优先安装作者 `requirements.txt`；不要因为论文标题含 AutoML 就自行安装某个未核验版本并称作者环境。

```bash
cd ../upstream/A03-benchmark-al-mat
mamba create -n repro-A03 python pip -y
mamba activate repro-A03
python -m pip install -r requirements.txt
python src/main.py --help
conda env export --from-history > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A03/environment.from-history.yml
python -m pip freeze > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A03/pip-freeze.txt
```

正式 AutoML 层必须从论文/作者补充材料确认版本、单轮时间预算和硬件后，另建 `environment.automl.yml`；禁止猜测。

## T0｜来源与入口核验

1. 核对 `dataset/meta.csv` 只有 `uci-concrete`，并记录当前仓库与论文“9 数据集”的差异。
2. 检查 `src/main.py` 的策略注册表、初始样本 10、每轮默认 10、阈值 0.85。
3. 审计 `src/utils/active_learner.py`：确认当前输出是否含真实 \(R^2\)/MAE；若只含查询索引，写入 `deviations.md`。

## T1｜最小 smoke test

```bash
cd ../upstream/A03-benchmark-al-mat/src
python main.py --random-state 42 --strategy RandomSearch \
  --dataset uci-concrete --initial-method random --n-pro-query 10
python main.py --random-state 42 --strategy TreeBasedRegressor_Representativity \
  --dataset uci-concrete --initial-method random --n-pro-query 10
python main.py --random-state 42 --strategy RD_GS_ALR \
  --dataset uci-concrete --initial-method random --n-pro-query 10
```

成功标准：三种策略退出码为 0、输出 JSON 可解析、查询索引无重复且预算一致。若 JSON 没有论文指标，只能标记“采样 smoke 成功”。

## T2｜忠实复现论文主结果

1. 先从论文或作者取得/重建明确的 Auto-sklearn 评估层、时间预算和九个固定数据版本。
2. 每轮以相同时间预算重新训练代理；保存 MAE、\(R^2\)、模型管线、拟合时间和查询索引。
3. 种子使用论文的 30–49（20 次），每轮新增 10；复现 MAE AUC、达到最大 \(R^2\) 60/70/80/90% 的标签数及置信区间。
4. 完整覆盖 17 AL＋Random 和 9 数据集。缺一个来源或 AutoML 配置时，T2 保持 `blocked`，不得用当前轻量代码结果替代论文主表。

## T3｜统一协议与消融

- 先做 Concrete 的 Random/Tree-based-R/RD-GS 三策略、5 个种子和短 AutoML 预算，随后恢复论文预算。
- 同时跑固定 RandomForest 代理，分离“查询策略收益”与“AutoML 每轮搜索收益”。
- 比较 random/kmeans 初始集；所有策略共享每个种子的初始索引和测试集。

## T4｜迁移至 DGEBA

- 将 DGEBA 表增加到独立 `meta.csv` 副本，明确目标 Y1 和允许输入列；不改上游原文件。
- 先以 Random/Tree-based-R/RD-GS 和固定 RF 代理跑离线 Synthetic oracle，再决定是否投入 AutoML。
- 使用 IL/多酚结构对分组留出；目标生成中间量和其他预测性能列不得作为输入。

## 公平性与评价

- 主指标：测试 MAE、\(R^2\)、MAE 学习曲线 AUC、达到相对 \(R^2\) 阈值所需标签数；报告 20 次置信区间。
- Random 必须存在；同一数据、划分、初始集、batch=10、总预算和 AutoML 时间预算。
- 预处理和 AutoML 搜索只用当前已标记训练集；测试集只评估，不能用于 early stop/选策略。
- 数据集间不得复用测试反馈调参；材料组成/批次/结构近重复需分组拆分。

## 证据交付

```text
reproduction/runs/A03/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── environment.automl.yml
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

`comparison.md` 必须区分“T1 当前仓库管线”与“T2 论文 AutoML 协议”。

## 停止条件

- smoke 成功：三策略查询轨迹有效且预算相同。
- 停止：当前 JSON 无指标却被当成论文复现、AutoML 版本/时间预算不明、九个数据未锁、策略异常后静默回退 Random（当前代码存在此风险）。
- 只有九数据、全部策略、种子 30–49、AutoML 配置、原始结果、论文表图核对及偏差说明齐全才可 `completed`。
