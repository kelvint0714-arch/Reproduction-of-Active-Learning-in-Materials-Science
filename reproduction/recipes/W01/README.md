# W01｜化学与材料分类策略数据效率复现路径

> 状态：`source-lock-needed`。作者提供“运行包”和“分析包”两个仓库；本文不声称已运行。

## 定位与边界

- 论文：*Data efficiency of classification strategies for chemical and materials design*，DOI：[10.1039/D4DD00298A](https://doi.org/10.1039/D4DD00298A)，*Digital Discovery* 2025, 4, 135–148。
- 分类：分类 AL/空间填充基准，不是 BO；31 个化学/材料分类任务、100 个模型×选样组合。
- 最小复现：`princeton` 单任务，Random 空间填充与 RF/NN 不确定性 AL。
- 忠实复现：31 任务、全部策略、30 seeds、0–10 轮，重建论文各图和朴素基线换算。
- 门槛：RF 单任务 CPU；GPC/NN/100 策略×31×30 计算量大，建议作业阵列/GPU。

## 来源锁定

- 运行代码与 31 任务：[webbtheosim/classification-suite](https://github.com/webbtheosim/classification-suite)。
- 论文分析、处理结果和作图：[webbtheosim/classification-analysis](https://github.com/webbtheosim/classification-analysis)。

```bash
git clone https://github.com/webbtheosim/classification-suite.git ../upstream/W01-classification-suite
git clone https://github.com/webbtheosim/classification-analysis.git ../upstream/W01-classification-analysis
for d in ../upstream/W01-classification-suite ../upstream/W01-classification-analysis; do
  git -C "$d" remote -v
  git -C "$d" branch --show-current
  git -C "$d" describe --tags --always --dirty
  git -C "$d" rev-parse HEAD
  git -C "$d" status --short
done
find ../upstream/W01-classification-suite/src/ClassificationSuite/Tasks \
  -type f -print0 | sort -z | xargs -0 shasum -a 256
```

将两个 SHA、两个许可证（均需逐一核验）、任务文件哈希与访问日期写入
`reproduction/runs/W01/source_lock.md`。

## 环境

- 环境名：`repro-W01`。
- 优先使用 suite 的 `requirements.txt` 和可编辑安装；analysis 再装其清单。

```bash
mamba create -n repro-W01 python=3.11 pip -y
mamba activate repro-W01
python -m pip install -r ../upstream/W01-classification-suite/requirements.txt
python -m pip install -e ../upstream/W01-classification-suite
python -m pip install -r ../upstream/W01-classification-analysis/requirements.txt
python -m ClassificationSuite.run --help
python -m pip freeze > /ABS/PATH/reproduction/runs/W01/pip-freeze.txt
conda env export --from-history > /ABS/PATH/reproduction/runs/W01/environment.from-history.yml
```

当前 `run.py` 导入 `celluloid`，但 suite 清单未明确包含它；若环境报缺失，先记录再加依赖，不能静默修补。

## T0｜来源与入口核验

1. 核对实际入口是安装包中的 `ClassificationSuite.run`；README 的 `src/run.py` 路径可能与当前树不一致。
2. 固定 `Tasks/config.json`：大多数任务初始 10、batch 10、10 轮，个别任务 batch 2/3/6。
3. 核对 `results.pickle` 结构与每个结果 `(11,4)`：round、balanced accuracy、macro-F1、MCC。
4. 验证 analysis 的 baseline reshape 使用 30 seeds；把论文/代码的完整 seed 集列入 config。

## T1｜最小 smoke test

```bash
mkdir -p /ABS/PATH/reproduction/runs/W01/raw_results
python -m ClassificationSuite.run --scheme al --task princeton \
  --sampler random --model rf --seed 0 \
  --results_dir /ABS/PATH/reproduction/runs/W01/raw_results
python -m ClassificationSuite.run --scheme sf --task princeton \
  --sampler random --model rf --seed 0 \
  --results_dir /ABS/PATH/reproduction/runs/W01/raw_results
```

注意：AL 中 `sampler` 只决定初始集，后续由模型的 `recommend()` 用不确定性选点；`sf+random` 才是随机被动基线。成功标准是两个 `.npy` 均为 `(11,4)`、指标有限且轮数一致。

## T2｜忠实复现论文主结果

1. 对 31 个任务、30 seeds 运行论文全部 100 种分类策略；保存 `.npy` 原始文件。
2. 按作者 analysis 数据结构组装 `results.pickle`，不得只复制仓库成品。
3. 用 `fig3.py` 等脚本重算中间 pickle，再用 `plotter.py --fig N` 出图。
4. 核对 RF/NN AL 的数据效率、任务间差异、balanced accuracy/macro-F1/MCC 及朴素基线所需标签数。

## T3｜统一协议与消融

- 先固定 3 个任务×RF/NN×AL/Random-SF×5 seeds；然后扩到 30。
- 增加真正的“每轮随机增量”AL 基线，区别于每轮独立重采样的 `sf+random`。
- 表征消融：Mordred 10/20/100/all 与 Morgan；任务/预算完全相同。
- 增加固定 held-out 测试集版本；作者代码在全域（包含已标记点）评价，需与论文协议结果分开。

## T4｜迁移至 DGEBA

- 仅用于二分类/多分类目标，例如相分离风险、实验成功/失败、失效模式；连续强度仍用回归 AL。
- 对配方候选池比较 RF/NN 不确定性与 Random，按结构对分组留出。
- 标签必须来自真实实验或清楚标记的 Synthetic 类别；类别不平衡时以 macro-F1/MCC 为主。

## 公平性与评价

- 指标：balanced accuracy、macro-F1、MCC；数据效率：达到朴素基线同等 macro-F1 所需标签数。
- 所有方法共享任务、seed、初始索引、每任务 batch/round；至少 30 seeds 才对齐论文。
- Random 空间填充和随机逐轮采集要分开命名；RF/NN 超参搜索只使用已标记训练数据。
- 全域评价包含训练点可能乐观；T3 held-out 结果不得与论文原指标混在同一列。

## 证据交付

```text
reproduction/runs/W01/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

保存每个 seed 的 `.npy`、任务哈希和 analysis 聚合脚本版本。

## 停止条件

- smoke 成功：AL/SF 两个 `(11,4)` 结果可解析。
- 停止：入口/缺失依赖未记录、把 `sampler=random` 的 AL 误称随机逐轮、任务数据自动下载但未锁哈希、只用仓库成品冒充重算。
- 两仓库 SHA、31 任务哈希、100 策略×30 seeds、分析重算和论文图核对齐全后才可 `completed`。
