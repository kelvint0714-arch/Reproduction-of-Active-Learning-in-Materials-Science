# P02｜NIST Fe-Co-Ni 主动学习/贝叶斯优化基准复现

**路径状态**：`source-lock-needed`
**论文**：[Benchmarking active learning strategies for materials optimization and discovery](https://doi.org/10.1093/oxfmat/itac006)
**正式论文卡**：[`papers/bayesian_optimization/benchmarks/P02_NIST_FeCoNi_Benchmark.md`](../../../papers/bayesian_optimization/benchmarks/P02_NIST_FeCoNi_Benchmark.md)

## 定位与边界

论文使用 921 个 Fe-Co-Ni 薄膜组成、XRD/相信息、Kerr rotation 与 magnetic coercivity 做候选池回放。目标是尽快找到性质最大值，所以这里按**目标优化型 AL / BO 基准**管理。

- 最小复现：一个性质、Random/Exploration/Exploitation/EI、10 个重复。
- 忠实复现：两个性质、论文列出的采集函数、1 个随机初始点、完整预算、100 次重复与 normalized minimum regret。
- 普通电脑可运行；官方 GitHub 只是 starter functions，不含完整驱动和数据，必须把“作者代码”与“本项目补写驱动”分开。
- CAMEO 对照若没有相同实现/输入，只能标为未复现，不能用近似函数替代后声称忠实一致。

## 来源锁定

一手来源：

- OUP 正式论文 DOI：`10.1093/oxfmat/itac006`
- 作者 starter code：[alex-aa-wang/Benchmarking-Active-Learning-Starter](https://github.com/alex-aa-wang/Benchmarking-Active-Learning-Starter)
- NIST REMI 官方数据页：[Open Access Data—Fe-Co-Ni](https://pages.nist.gov/remi/data/)

```bash
git clone https://github.com/alex-aa-wang/Benchmarking-Active-Learning-Starter.git \
  ../upstream/P02-nist-fecotni-starter
git -C ../upstream/P02-nist-fecotni-starter remote -v
git -C ../upstream/P02-nist-fecotni-starter branch --show-current
git -C ../upstream/P02-nist-fecotni-starter describe --tags --always --dirty
git -C ../upstream/P02-nist-fecotni-starter rev-parse HEAD
git -C ../upstream/P02-nist-fecotni-starter status --short
shasum -a 256 ../upstream/P02-nist-fecotni-starter/LICENSE \
  ../upstream/P02-nist-fecotni-starter/methods2_9_5.py \
  ../upstream/P02-nist-fecotni-starter/helpers.py
```

从 NIST 页面跟随 **Fe-Co-Ni** 官方下载链接，保留原文件名、最终 URL、下载日期、HTTP header、许可/使用说明和 SHA-256：

```bash
shasum -a 256 ../upstream/P02-nist-fecotni-data/* \
  > reproduction/runs/P02/data_sha256.txt
```

所有信息写入 `reproduction/runs/P02/source_lock.md`。上游无 tag；必须记录实际 SHA。不要从非官方镜像补数据而不标注。

## 环境

环境名：`repro-p02-fecotni`。starter 无环境文件，已核验 import 包括 NumPy、SciPy、Matplotlib、TensorFlow、GPflow、Plotly 和 Google Colab。禁止凭年代猜一个“作者环境”。

```bash
conda create -n repro-p02-fecotni python=3.9 pip -y
conda activate repro-p02-fecotni
python -m pip install numpy scipy matplotlib plotly tensorflow gpflow
python -m pip check
python -m pip freeze > reproduction/runs/P02/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P02/environment.yml
```

Python 3.9 是兼容性探测选择而非论文声明，必须写进 `deviations.md`。若当前 TensorFlow/GPflow API 不兼容，先根据 commit 日期解析一个可导入的成对版本并锁定；不要直接改采集公式。完整环境优先 Linux x86_64。

## T0｜来源和数据核验

1. 审计 `methods2_9_5.py` 与 `helpers.py`，生成“函数—论文 Table 1 采集策略”映射。
2. 确认数据恰含 921 个候选；核对 Fe/Co/Ni 总和约束、单位、缺失值、重复组成、Kerr/magnetic coercivity 目标方向。
3. 从论文记录：1 个均匀随机初始点、每策略 100 次重复、候选不可重复、normalized minimum regret 定义。
4. 明确 starter 的 `methods` 列表中 `samy` 对应何种公式；只有公式逐项一致才标为 Add-GP-UCB。
5. 建立数据清洗与论文补充材料的逐项对照。

## T1｜最小 smoke test

先验证导入：

```bash
PYTHONPATH=../upstream/P02-nist-fecotni-starter \
python -c "import helpers, methods2_9_5; print(methods2_9_5.methods)"
```

随后在 `reproduction/runs/P02/configs/smoke.yaml` 固定 Kerr、1 个初始点、20 次查询、10 个配对种子，运行本项目驱动调用作者函数。输出每轮索引、均值、方差、采集分数和 minimum regret。

Smoke 成功要求：三元组成处理正确、已选点被 mask、无重复查询、随机策略无需拟合 GP、相同种子轨迹一致。

## T2｜忠实复现论文主结果

1. 对 Kerr rotation 和 magnetic coercivity 分别运行 Exploration、Exploitation、UCB、Add-GP-UCB、Thompson Sampling、EI、Random；CAMEO 只有在获得论文一致实现后纳入。
2. 使用论文的 isotropic RBF GP 与 Gaussian likelihood；任何核/噪声变化写入偏差。
3. 每个策略均从相同的 100 个初始点开始，并一直回放至论文预算/全池。
4. 计算每轮 normalized minimum regret 的均值与置信区间。
5. 核对论文图 3/4、达到全局最优 0.1% 范围的样本数，以及简单/复杂性质下的策略排序。

不要因为 starter 在命中最优后重复追加同一索引就把重复点当成新实验；结果存储可按论文逻辑保持 best-so-far，但查询计数必须审计。

## T3｜统一协议与消融

- 用显式 simplex 两坐标与三组成坐标分别拟合，检查共线性处理。
- 比较 RBF length scale、观测噪声、输入归一化和一次/批量选择。
- 以固定配对种子报告 Random、EI、UCB、TS 的 median regret、AUC-regret 和命中概率。
- 做错误/缺失相区先验消融，区分物理先验收益与采集函数收益。
- 评估 GP 区间覆盖率；测试集或全池标签不得用于调 acquisition 超参。

## T4｜迁移到 DGEBA/粘合剂数据

P02 最适合迁移的是“不同地形需要不同采集策略”的基准方法，而不是 Fe-Co-Ni 特征本身。先固定一种离子液体—多酚结构对并获得多个真实配比点，再比较 Greedy、EI、UCB、TS；如果结构对同时变化，必须把结构表示纳入并做结构分组验证。

当前 Synthetic 表只能作离线 Oracle 演练。每个结构对只有一个配比时，不能拟合该结构对的小数配比峰谷，也不能将 12 个跨结构均值当成真实响应面。

## 公平性与评价

- 论文主指标：normalized minimum regret、到达 0.1% 最优范围的查询数、命中率、regret AUC。
- 每策略共享同一初始点、预算和种子；论文级复现为 100 次重复。
- Random、纯探索和纯利用均为必要基线。
- 两个目标必须分开评价，不能用 Kerr 上选出的策略再无代价地宣称适合 coercivity。
- 组成缩放只使用特征，不接触目标；目标归一化参数只能由当前已标注集得到。
- 审计重复组成、三元闭合约束、相区信息泄漏和全局最优偷看。

## 证据交付

```text
reproduction/runs/P02/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── data_sha256.txt
├── method_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

额外保存驱动器版本、100 个初始索引和每轮候选表；作者代码与本项目驱动输出分目录保存。

## 停止条件

- Smoke 成功：一个目标、四种策略、10 个种子完成且无重复选点/泄漏。
- 立即阻塞：NIST 数据版本或许可无法确认、数据行数/单位与论文不符、采集公式映射不清、TensorFlow 修复改变算法语义。
- 只有两个目标、论文策略、100 次重复、原始轨迹、图 3/4 核对、环境与偏差齐全后才可标为 `completed`；缺 CAMEO 时必须注明部分复现。
