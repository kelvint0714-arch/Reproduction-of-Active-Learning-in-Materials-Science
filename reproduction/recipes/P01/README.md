# P01｜PV-Lab 跨材料领域贝叶斯优化基准复现

**路径状态**：`source-lock-needed`
**论文**：[Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains](https://doi.org/10.1038/s41524-021-00656-9)
**正式论文卡**：[`papers/bayesian_optimization/benchmarks/P01_PVLab_Benchmarking.md`](../../../papers/bayesian_optimization/benchmarks/P01_PVLab_Benchmarking.md)

## 定位与边界

这是候选池上的**贝叶斯优化（BO）离线回放**，不是以降低全局预测误差为唯一目标的模型学习型主动学习。完整数据只充当 Oracle；未被查询的标签在每轮选择前必须隐藏。

- 最小复现：在 `Crossed barrel` 上运行 Random、GP-RBF+EI 和 RF+Greedy，产出查询轨迹与 top-5% recovery。
- 忠实复现：使用作者五个数据集、GP 各向同性/ARD 与 RF 代理、论文采集函数和作者重复协议，核对论文加速/增强指标。
- 普通电脑可完成小数据集回放；Notebook 的 GPy/GPyOpt 依赖较旧，Apple Silicon 可能需要 Linux x86_64 容器。
- 本路径不声称复现真实自动化实验，也不把一次成功轨迹当作论文级结果。

## 来源锁定

一手来源：

- 论文 DOI：`10.1038/s41524-021-00656-9`
- 作者代码和五个 CSV：[PV-Lab/Benchmarking](https://github.com/PV-Lab/Benchmarking)
- 官方入口：`Example use of framework with GP type surrogate models.ipynb`、`Example use of framework with RF type surrogate models.ipynb`
- 上游没有 tag/release；第一次运行必须把 `main` 解析为 SHA。GitHub 元数据与 README 对许可证名称的显示可能不一致，必须以实际 `LICENSE` 文件为准。

```bash
git clone https://github.com/PV-Lab/Benchmarking.git ../upstream/P01-pvlab-benchmarking
git -C ../upstream/P01-pvlab-benchmarking remote -v
git -C ../upstream/P01-pvlab-benchmarking branch --show-current
git -C ../upstream/P01-pvlab-benchmarking describe --tags --always --dirty
git -C ../upstream/P01-pvlab-benchmarking rev-parse HEAD
git -C ../upstream/P01-pvlab-benchmarking status --short
shasum -a 256 ../upstream/P01-pvlab-benchmarking/LICENSE
find ../upstream/P01-pvlab-benchmarking/datasets -type f \
  -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/P01/data_sha256.txt
```

把命令、访问日期、SHA、许可证正文标题、数据哈希和论文 DOI 写入
`reproduction/runs/P01/source_lock.md`。不得只记录 `main`。

## 环境

环境名：`repro-p01-pvlab`。上游只给出未固定版本的 `requirements.txt`，且 Notebook 还导入其中未列出的 `torch`、`GPyOpt`、`seaborn`、`python-ternary`。因此不能把随意选择的现代版本冒充作者环境。

1. 先从锁定 Notebook 的 metadata 和 import 列表生成 `dependency_audit.md`。
2. 在 Linux x86_64 隔离环境中做兼容性探测；Python 版本属于本项目选择，写入 `deviations.md`。
3. 安装成功后保存解析后的完整环境，而不是回写猜测版本：

```bash
conda create -n repro-p01-pvlab python=3.8 pip jupyter -y
conda activate repro-p01-pvlab
python -m pip install -r ../upstream/P01-pvlab-benchmarking/requirements.txt
python -m pip install torch GPyOpt seaborn python-ternary
python -m pip check
python -m pip freeze > reproduction/runs/P01/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P01/environment.yml
python - <<'PY' > reproduction/runs/P01/hardware.txt
import platform
print(platform.platform())
print(platform.machine())
print(platform.python_version())
PY
```

若 GPy/GPyOpt 无法安装，优先使用容器保留原 Notebook；用 scikit-learn 重写只能放在 T3，不能冒充 T2。

## T0｜来源和入口核验

1. 建立 `reproduction/runs/P01/` 标准目录。
2. 完成来源锁定与五个 CSV 的列名、行数、重复行、缺失值和目标方向审计。
3. 用 `jupyter nbconvert --to script` 导出两个 Notebook，记录其真实参数。已核验的 GP Notebook 默认示例包括 `n_initial=2`、top 5% 定义和 `n_ensemble=50`；仍须以锁定 SHA 为最终依据。
4. 建立“Notebook 单元格—论文图/表—输出文件”映射，确认每个数据集的最大化/最小化方向。

T0 交付：`source_lock.md`、`dependency_audit.md`、`data_audit.csv`、`figure_map.md`。任何 CSV 无法读取或许可证不允许当前用途时停止。

## T1｜最小 smoke test

在工作副本中把数据路径显式指向
`datasets/Crossed barrel_dataset.csv`，只运行一个固定种子、2 个初始点和小预算：

```bash
jupyter nbconvert --execute \
  --ExecutePreprocessor.timeout=1800 \
  --to notebook \
  --output-dir reproduction/runs/P01/raw_results \
  --output gp_crossed_barrel_smoke.ipynb \
  "../upstream/P01-pvlab-benchmarking/Example use of framework with GP type surrogate models.ipynb"
```

如果必须修改 Notebook，保存 patch 到 `reproduction/runs/P01/configs/`，绝不覆盖上游。Smoke 成功要求：无重复查询、未查询标签未进入拟合/采集、每轮输出所选索引与 best-so-far、同种子可重复。

## T2｜忠实复现论文主结果

1. 对五个官方数据集分别运行作者 GP 和 RF Notebook。
2. 保持作者初始集、目标符号、核/ARD 开关、采集函数、预算、top 5% 定义和重复次数；若论文与 Notebook 不一致，以论文为主并记录差异。
3. 至少复现 Random、Greedy、EI、PI、置信界，以及 GP-isotropic、GP-ARD、RF 的论文组合。
4. 保存每轮 `candidate_id`、预测均值、预测尺度、采集分数、选中点、已知最优和全局最优（全局最优只用于事后评价）。
5. 重画 top-5% recovery、best-so-far/normalized regret、acceleration 与 enhancement；以重复的均值和置信区间核对论文图。

T2 不允许为了更好结果调种子，也不能用测试标签选择核、采集函数或停止轮次。

## T3｜统一协议与消融

在不改 T2 原始结果的前提下，用统一驱动器进行：

- Random、Greedy、EI、UCB 在完全相同初始集/预算上的配对比较；
- GP isotropic vs GP-ARD vs RF；
- 初始样本数、batch size、噪声和特征标准化消融；
- RF 树间标准差与 GP 后验标准差的校准比较；
- 结构/配方近邻分组划分，检查相似候选泄漏。

统一报告 median、IQR、95% bootstrap CI、成功率和 paired seed 差值；全局预测 MAE/RMSE 只能作为辅助指标。

## T4｜迁移到 DGEBA/粘合剂数据

把每一行真实可实验配方视为离散候选，先预测一个实测目标（建议低温剪切强度）。只使用实验前已知的结构/配方/工艺特征，排除由合成标签生成的 `Crosslink_density`、`Predicted_Tg`、`Predicted_modulus`、`Compatibility_Index`、`Phase_Separation_Risk`、`Network_Toughness_Index`。

先做离线 Synthetic Oracle 演练，并明确标记“流程验证”；真实结论必须等待化学组回填。按离子液体/多酚结构对分组划分，不能让同一或高度相似结构同时出现在训练和测试。当前每个结构对仅一个配比时，不得据此宣称连续比例最优。

## 公平性与评价

- 初始候选集合、种子、预算、batch size 必须跨策略共享；优先配对比较。
- BO 主指标：simple/normalized regret、best-so-far、top-k recovery、达到 top 1%/5% 的查询数、成功率和墙钟时间。
- 模型辅助指标：固定测试集 MAE/RMSE、负对数似然、区间覆盖率/校准；不能用 MAE 代替 BO 成功率。
- Random 是必需基线；Greedy 用来分离纯利用贡献。
- 预处理只能在当前已标注集拟合；不得用全池标签做缩放、超参选择或早停。
- 重复候选、近邻配方、时间顺序和结构家族必须审计；Oracle 标签只在查询后揭示。

## 证据交付

```text
reproduction/runs/P01/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── dependency_audit.md
├── data_sha256.txt
├── data_audit.csv
├── figure_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

`comparison.md` 必须逐项给出论文图/表、作者值、本次统计量、容差、是否一致；`deviations.md` 记录所有路径修复、依赖替换和参数差异。

## 停止条件

- Smoke 成功：一个数据集、一个种子完成闭环，轨迹长度正确、无重复选点、无标签泄漏且结果可重跑。
- 立即阻塞：数据哈希不稳、目标方向不明、依赖修复改变算法、Notebook 读取全池标签参与决策，或无法确认许可证。
- 仅当五个数据集的来源、环境、配置、全部种子、原始轨迹、统计图、论文核对与偏差说明齐全，才可把状态改为 `completed`。
