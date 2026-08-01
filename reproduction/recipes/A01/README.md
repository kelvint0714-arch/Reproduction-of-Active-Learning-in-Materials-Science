# A01｜NIST 微结构—性能主动学习复现路径

> 状态：`source-lock-needed`。本文是执行手册，不代表任何结果已在本机运行。

## 定位与边界

- 论文：*Active learning for regression of structure–property mapping: the importance of sampling and representation*，DOI：[10.1039/D4DD00073K](https://doi.org/10.1039/D4DD00073K)。
- 分类：模型学习型主动学习（AL），不是寻找性质极值的 BO。
- 目标：用 GPR 比较 Random、最大预测方差、GSx、GSy、iGS，并检验微结构表征对固定测试集 MAE 的影响。
- 最小复现只跑作者仓库的 `2D/` 弹性数据；忠实复现还包括 3D 和 OPV 工作流、20 次重复及分布指标。
- 门槛：2D smoke test 可用 CPU；3D 物理计算、完整 20 次重复耗时显著。仓库数据使用 Git LFS，必须先安装 `git-lfs`。

## 来源锁定

- 官方代码/二维与三维数据：[usnistgov/active-learning](https://github.com/usnistgov/active-learning)。
- OPV 工作流：[hliu56/Active-Learning-Using-various-representations](https://github.com/hliu56/Active-Learning-Using-various-representations)。
- 相关数据归档：[Zenodo 10.5281/zenodo.7562957](https://doi.org/10.5281/zenodo.7562957)。

第一次执行时从本仓库根目录运行；不要只记录 `main`：

```bash
git lfs install
git clone https://github.com/usnistgov/active-learning.git ../upstream/A01-nist-active-learning
git -C ../upstream/A01-nist-active-learning lfs pull
git -C ../upstream/A01-nist-active-learning remote -v
git -C ../upstream/A01-nist-active-learning branch --show-current
git -C ../upstream/A01-nist-active-learning describe --tags --always --dirty
git -C ../upstream/A01-nist-active-learning rev-parse HEAD
git -C ../upstream/A01-nist-active-learning status --short
shasum -a 256 ../upstream/A01-nist-active-learning/2D/data-gen/*.npz
```

把输出、访问日期、`LICENSE` 内容摘要和数据哈希写入
`reproduction/runs/A01/source_lock.md`。若继续复现 OPV，单独克隆并锁定第二个仓库，不把两个仓库的 SHA 混为一个。

## 环境

- 环境名：`repro-A01`。
- 优先使用作者的 `environment.yml`，不得用根目录的绝对路径型 `requirements.txt` 猜测新环境。

```bash
cd ../upstream/A01-nist-active-learning
mamba env create -n repro-A01 -f environment.yml
mamba activate repro-A01
snakemake --version
python -c "import sklearn, dask; print(sklearn.__version__, dask.__version__)"
conda env export --from-history > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A01/environment.from-history.yml
conda list --explicit > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A01/environment.explicit.txt
```

另记录操作系统、CPU、内存、是否使用 GPU、`git-lfs version`；若 `pymks@flakes` 无法安装，先停止并记录，不要静默换包。

## T0｜来源与入口核验

1. 确认 `2D/config.yaml`（不是 README 中误写的 `config.yml`）、`2D/Snakefile`、`2D/data-gen/*.npz` 均存在且 LFS 文件不是指针文本。
2. 运行 `snakemake -n --cores 1` 检查 DAG，不产生正式结果。
3. 把论文的 2D 数据规模、初始集、`n_query`、`n_iterations`、核函数和评分方式逐项抄入 `configs/paper_2d.yaml`，保留原 `config.yaml`。

## T1｜最小 smoke test

复制配置到运行目录，将 `n_iterations` 改为 `1`、设置新的 `job_name`，然后：

```bash
cd ../upstream/A01-nist-active-learning/2D
snakemake --cores 1
```

成功标准：工作流退出码为 0，生成运行目录、配置快照和 `plot.pdf`（或当前工作流声明的等价 PDF），Random 与至少一种 AL 曲线可读取；这只证明管线可运行。

## T2｜忠实复现论文主结果

1. 恢复论文配置；Random、variance、GSx、GSy、iGS 使用相同池、初始索引、预算与测试集。
2. 按论文做 20 次重复，保存每次查询索引，而不只保存均值曲线。
3. 复现测试 MAE—标签数曲线、80% 改善所需标签数、Wasserstein 距离、熵和池平均不确定性。
4. 分别复现图描述符与两点相关函数＋PCA；最后才扩展至 3D/OPV。

## T3｜统一协议与消融

- 固定 5 个公共种子做快速协议，再扩为论文 20 次；对所有策略复用每个种子的初始集。
- 消融：表征固定只改采样策略；采样固定只改表征；另报告全数据监督上限。
- 增加结构族分组留出，比较随机划分与结构外推，防止近重复微结构跨池/测试集。

## T4｜迁移至 DGEBA

- 把一行配方视为池样本，先用实验前可得的离子液体/多酚描述符和 loading；Y1 作为第一目标。
- 固定独立测试集，比较 Random、最大方差、iGS；每轮只从训练池“揭示” Synthetic 标签。
- 排除 `Crosslink_density`、`Predicted_Tg`、`Predicted_modulus`、`Compatibility_Index`、`Phase_Separation_Risk`、`Network_Toughness_Index` 等可能由目标生成的字段。
- 该阶段只验证离线 AL 流程；没有真实实验 oracle 时不得写成发现真实最优胶黏剂。

## 公平性与评价

- 主指标：固定测试集 MAE；辅指标：RMSE、\(R^2\)、80% 改善标签数、学习曲线 AUC、Wasserstein 距离、熵、平均不确定性。
- 记录划分、初始索引、逐轮查询索引、预算、batch size、种子和 20 次均值/标准差。
- Random 是必要基线；全数据 GPR 是性能上限。测试集只用于评估，不得参与 PCA 拟合、超参数选择或采集。
- 表征变换仅在训练池拟合；按结构来源去重，避免 2D/3D 或同族近重复泄漏。

## 证据交付

```text
reproduction/runs/A01/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── environment.explicit.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

`comparison.md` 逐图核对论文样本预算、均值、误差带和趋势；`deviations.md` 记录 LFS、依赖、数据或配置改动。

## 停止条件

- smoke 成功：T1 输出完整且可解析。
- 立即停止：LFS 数据缺失/哈希变化、无法建立作者环境、划分或论文参数无法确认、测试集进入采集。
- 只有固定 SHA、数据哈希、环境、20 次原始结果、处理脚本、图表核对和偏差说明齐全，才能改为 `completed`。
