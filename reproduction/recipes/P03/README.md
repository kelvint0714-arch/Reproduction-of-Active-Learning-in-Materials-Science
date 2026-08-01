# P03｜Bgolearn 统一材料贝叶斯优化框架复现

**路径状态**：`recipe-ready`
**论文**：[Bgolearn: a unified Bayesian optimization framework for accelerating materials discovery](https://doi.org/10.1038/s41524-026-02226-3)
**正式论文卡**：[`papers/bayesian_optimization/frameworks/P03_Bgolearn.md`](../../../papers/bayesian_optimization/frameworks/P03_Bgolearn.md)

## 定位与边界

Bgolearn 是材料 BO 工具框架，可组合代理模型和采集函数；“成功调用推荐接口”是软件 smoke test，不等于论文算法贡献或材料发现结论已经复现。

- 最小复现：官方 `singleobject_regression/code.ipynb`，固定数据上输出下一候选。
- 忠实复现：锁定论文对应版本，复现论文/CodeDemo 指定案例和推荐结果。
- 普通电脑可完成单目标表格案例；PES/KG、多目标和大候选池可能更慢。
- 非 GP 模型的不确定性必须从锁定代码确认，不能默认 RF/MLP 输出 GP 后验。

## 来源锁定

一手来源：

- 论文 DOI：`10.1038/s41524-026-02226-3`
- 主仓库：[Bin-Cao/Bgolearn](https://github.com/Bin-Cao/Bgolearn)，MIT
- 官方示例数据：[Bgolearn/CodeDemo](https://github.com/Bgolearn/CodeDemo)
- 官方文档：[bgolearn.netlify.app](https://bgolearn.netlify.app/)
- 已核验主仓库存在 release/tag `V3.1.0`；CodeDemo 暂无 tag，需另锁 SHA。

```bash
git clone --branch V3.1.0 --depth 1 \
  https://github.com/Bin-Cao/Bgolearn.git ../upstream/P03-bgolearn
git clone https://github.com/Bgolearn/CodeDemo.git ../upstream/P03-bgolearn-codedemo
git -C ../upstream/P03-bgolearn remote -v
git -C ../upstream/P03-bgolearn describe --tags --always --dirty
git -C ../upstream/P03-bgolearn rev-parse HEAD
git -C ../upstream/P03-bgolearn-codedemo branch --show-current
git -C ../upstream/P03-bgolearn-codedemo rev-parse HEAD
git -C ../upstream/P03-bgolearn-codedemo status --short
shasum -a 256 ../upstream/P03-bgolearn/LICENSE
find ../upstream/P03-bgolearn-codedemo -type f \
  \( -name '*.csv' -o -name '*.xlsx' -o -name '*.joblib' \) \
  -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/P03/data_sha256.txt
```

在 `reproduction/runs/P03/source_lock.md` 同时记录 PyPI `Bgolearn==3.1.0` 的 wheel/sdist 哈希：

```bash
python -m pip download --no-deps Bgolearn==3.1.0 \
  --dest reproduction/runs/P03/source_packages
shasum -a 256 reproduction/runs/P03/source_packages/*
```

若 tag 与 PyPI 版本内容不一致，T2 以论文声明版本为准并记录差异。

## 环境

环境名：`repro-p03-bgolearn`。优先使用发布包，避免把仓库 `main` 的未来修改混入。

```bash
conda create -n repro-p03-bgolearn python=3.10 pip jupyter -y
conda activate repro-p03-bgolearn
python -m pip install Bgolearn==3.1.0 pandas openpyxl
python -m pip check
python -m pip show Bgolearn > reproduction/runs/P03/bgolearn-package.txt
python -m pip freeze > reproduction/runs/P03/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P03/environment.yml
```

Python 3.10 是本路径的运行选择；若包元数据要求其他版本，以锁定 tag/PyPI metadata 为准。不要凭 README 的模型列表自行安装未被包声明的后端。

## T0｜来源、API 与数据核验

1. 对 tag、PyPI 和 CodeDemo SHA 做来源锁定。
2. 审计 `singleobject_regression/code.ipynb`、`data/train.xlsx` 的列含义、目标方向和输出文件。
3. 建立代理模型—不确定性实现—可用采集函数表；逐项确认 GP、SVM、RF、AdaBoost、MLP 的置信尺度来源。
4. 记录每个 API 默认值、随机种子、标准化、噪声和候选重复处理。
5. 将 TPMS 论文案例与公开数据的对应关系写入 `figure_map.md`；无法对应时不声称论文级 TPMS 复现。

## T1｜最小 smoke test

```bash
python -c "import Bgolearn; print(Bgolearn.__file__)"
jupyter nbconvert --execute \
  --ExecutePreprocessor.timeout=1800 \
  --to notebook \
  --output-dir reproduction/runs/P03/raw_results \
  --output singleobject_smoke.ipynb \
  ../upstream/P03-bgolearn-codedemo/singleobject_regression/code.ipynb
```

保留原始 `train.xlsx`，将包生成的推荐 CSV 复制到 `raw_results/` 并记录运行前后文件清单。Smoke 成功要求：包可导入、Notebook 完成、推荐候选属于未测试池、方向正确且输出包含可追踪采集分数。

## T2｜忠实复现论文主结果

1. 优先运行论文明确对应的官方案例；若 TPMS 的“50 个初始、5000 个候选、每轮 2 个、两轮验证”数据未完整公开，明确标为不可完整复现。
2. 在官方单目标案例上保持数据、代理、噪声、目标方向和采集参数不变，核对推荐排序。
3. 对论文列出的 EI/AEI/EQI/REI/UCB/PoI/PES/KG，只复现有明确官方入口和参数的结果。
4. 保存训练均值、预测不确定性、采集分数、推荐列表和实际/离线 Oracle 回填。
5. 框架输出必须与论文表/图逐项映射；软件功能展示不得替代论文主实验。

## T3｜统一协议与消融

- 在同一候选池、初始集、预算和种子下比较 Random、Greedy、GP-EI、GP-UCB。
- 再比较两个代理模型；若非 GP 模型的不确定性不可校准，不运行依赖概率分布的 EI，或清楚标为框架定义。
- 对噪声已知/未知、batch size、归一化和目标方向做消融。
- 用 30 个以上配对种子报告 regret AUC、命中率、墙钟时间和不确定性覆盖率。
- 输出包默认值与显式配置的差异，避免“默认漂移”。

## T4｜迁移到 DGEBA/粘合剂数据

准备三张不可混用的表：已实验训练集、可实际制备候选池、独立测试集。第一版只用实验前可知特征预测一个目标，排除合成标签派生中间量；以 Random、Greedy、GP-EI、GP-UCB 比较离线 Synthetic Oracle。

Bgolearn 可以推荐当前**离散候选池**，不能凭 12 个跨结构平均配比点直接制造连续小数最优。只有固定结构对并获得足够真实配比—性能点后，才能构造连续比例候选和实验回填。

## 公平性与评价

- BO 指标：simple/normalized regret、best-so-far、达到 top 1%/5% 的查询数、成功率、累计实验成本。
- 多目标时报告 hypervolume、Pareto recall/precision 和可行率；不能把多个目标先随意加权再称 EHVI。
- Random 和 Greedy 必须存在；所有方法共享初始点、预算、batch 和种子。
- 不确定性评价：NLL、区间覆盖率与校准；不同代理的尺度不可直接等同。
- 数据预处理仅在已标注集拟合；候选标签在查询前隐藏。
- 结构、时间、批次和重复配方泄漏必须单独审计。

## 证据交付

```text
reproduction/runs/P03/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── bgolearn-package.txt
├── source_packages/
├── data_sha256.txt
├── figure_map.md
├── model_uncertainty_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

## 停止条件

- Smoke 成功：官方单目标 Notebook 无错运行，推荐点合法、输出可追踪且同配置可重跑。
- 立即阻塞：tag/PyPI 不一致且无法判定论文版本、目标方向不明、非 GP 不确定性来源不清却被用于 EI、示例数据许可不明。
- 只有论文对应案例、版本、环境、配置、原始输出、统计比较与偏差齐全，才能标 `completed`；只跑通包保留 `recipe-ready`。
