# P06｜MolPAL 分子候选池批量 BO 复现

**路径状态**：`recipe-ready`
**论文**：[Accelerating high-throughput virtual screening through molecular pool-based active learning](https://doi.org/10.1039/D0SC06805E)
**正式论文卡**：[`papers/related/molecular_bo/P06_MolPAL.md`](../../../papers/related/molecular_bo/P06_MolPAL.md)

## 定位与边界

MolPAL 在巨大 SMILES 候选池中用代理模型和批量采集减少昂贵评分次数。论文称 pool-based active learning，评价却是 top-k 高分分子的找回效率，因此本路径按**批量 BO 式分子筛选**管理。

- 最小复现：官方 `Enamine10k` lookup Oracle，RF+Random 与 RF+Greedy。
- 忠实复现：固定 `publication` tag，按 `config_expts` 回放 10k/50k 及论文指定大池配置，比较 RF、FFN、MPNN 与采集策略。
- 10k/50k 可在普通电脑运行；MPNN 建议 GPU。2M/100M 分子与在线 docking 需要服务器/集群、存储、外部 docking 软件和可能的许可证。
- lookup 得分是离线 Oracle，不等于重新执行分子对接或湿实验。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1039/D0SC06805E`
- 作者仓库：[coleygroup/molpal](https://github.com/coleygroup/molpal)，MIT
- 论文冻结 tag：`publication`
- tag 内自带 `libraries/Enamine10k.csv.gz`、`libraries/Enamine50k.csv.gz`、lookup 分数和实验配置；AmpC 大表由作者指向 Figshare。

```bash
git clone --branch publication --depth 1 \
  https://github.com/coleygroup/molpal.git ../upstream/P06-molpal
git -C ../upstream/P06-molpal remote -v
git -C ../upstream/P06-molpal branch --show-current
git -C ../upstream/P06-molpal describe --tags --always --dirty
git -C ../upstream/P06-molpal rev-parse HEAD
git -C ../upstream/P06-molpal status --short
shasum -a 256 ../upstream/P06-molpal/LICENSE \
  ../upstream/P06-molpal/environment.yml
find ../upstream/P06-molpal/libraries ../upstream/P06-molpal/data \
  -type f -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/P06/data_sha256.txt
```

Figshare/AmpC 只在 T2 需要时下载；记录 DOI/落地 URL、许可和哈希，不把没有再分发许可的大文件提交本仓库。来源写入 `reproduction/runs/P06/source_lock.md`。

## 环境

环境名使用作者文件中的 `molpal`。`publication/environment.yml` 已核验指定 Python 3.8、CUDA 11.1、PyTorch、RDKit、Ray、TensorFlow 等。

```bash
conda env create -f ../upstream/P06-molpal/environment.yml
conda activate molpal
python -m pip check
python -m pip freeze > reproduction/runs/P06/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P06/environment.yml
python - <<'PY' > reproduction/runs/P06/hardware.txt
import platform
print(platform.platform(), platform.machine())
try:
    import torch
    print("torch", torch.__version__, "cuda", torch.cuda.is_available())
except Exception as exc:
    print("torch import failed:", repr(exc))
PY
```

CPU smoke 可在环境副本删除 `cudatoolkit`，但必须保存环境 diff。Apple Silicon 若旧 TensorFlow/Ray 不兼容，优先 Linux x86_64；不得用 main 分支替代 publication 后仍称忠实复现。

## T0｜来源、配置与分子数据核验

1. 固定 `publication` tag 的 SHA、环境、许可证和所有自带数据哈希。
2. 用 RDKit 检查 SMILES 可解析率、重复 canonical SMILES、lookup 标签缺失与目标方向（docking score 通常最小化）。
3. 解析 `config_expts/Enamine10k_*`、`Enamine50k_*`，记录初始比例、batch 比例、模型、指纹、采集函数、重训方式和停止条件。
4. 建立 `model_uncertainty_map.md`：RF 树间、NN/MPN 的 ensemble/dropout/MVE 与 `none` 分别如何进入 UCB/EI。
5. 确认论文每张图对应哪个配置和 `scripts/analyze_data.py` 参数。

## T1｜最小 smoke test

先关闭 GPU，使用官方 10k lookup 配置的副本，限定两个 epoch：

```bash
export CUDA_VISIBLE_DEVICES=''
cd ../upstream/P06-molpal
python run.py \
  --config config_expts/Enamine10k_retrain.ini \
  --name p06_rf_greedy_smoke \
  --metric greedy \
  --model rf \
  --max-epochs 2
```

再以相同初始 seed 运行 `--metric random`。将配置、stdout 和输出目录复制至 `reproduction/runs/P06/`。Smoke 成功要求：10k 池载入、指纹缓存生成、查询不重复、lookup 只在被选后返回标签、每轮 top-k recovery 有记录。

## T2｜忠实复现论文主结果

1. 直接使用 `publication/config_expts/`，不混入 main 的新 CLI。
2. 先复现 Enamine10k/50k 的 retrain/online 设置，再按资源决定是否复现 EnamineHTS、AmpC。
3. 对 RF、FFN、MPNN 和 Random/Greedy/UCB 等论文组合使用相同初始集、batch size、预算与重复种子。
4. 保存每轮查询 SMILES、真实 lookup 分数、预测均值/置信度、采集值、top-k recovery 与运行耗时。
5. 按作者目录结构整理输出，用 `scripts/make_dict.py` 和 `scripts/analyze_data.py` 重画论文曲线。
6. 无法承担大池资源时，明确标注“10k/50k 部分复现”，不要外推亿级加速。

## T3｜统一协议与消融

- 在同一 10k 池上配对比较 Random、Greedy、UCB、EI，以及 RF/FFN/MPNN。
- 固定 ECFP 类型、长度 2048、radius 2 后比较模型；再单独做指纹消融。
- 报告每轮 top-100/top-1% recovery、EF、precision、采样比例、模型时间和 Oracle 时间。
- 按 Bemis–Murcko scaffold 分析回收率，避免只找回同一骨架近邻。
- 对 batch size、重训频率、不确定性方法和批内去重/多样性做消融。

## T4｜迁移到 DGEBA/粘合剂数据

只有候选具有可靠 canonical SMILES/分子图时才直接使用 MolPAL。多组分配方不能只画成一个单分子：应分别编码树脂、固化剂、离子液体、多酚，再拼接比例和工艺特征，或设计 mixture graph。

第一版用 RF+ECFP 拼接做强基线，并把真实实验表作为 lookup Oracle。当前 Synthetic 表只用于接口测试；SMILES 缺失、盐/离子对表示不稳定或每个结构仅一个配比时，停止 GNN 结论。比较 Random/Greedy/UCB，报告结构家族回收率而非只报训练误差。

## 公平性与评价

- 主指标：top-k recovery、enrichment factor、达到 50%/80% top-k recovery 的采样比例、best-so-far 和墙钟/Oracle 成本。
- Random 与 Greedy 是必需基线；所有模型共享初始 SMILES、batch、预算和种子。
- scaffold split 只用于模型泛化辅助评价；候选池 BO 仍需保存完整顺序轨迹。
- canonical SMILES 去重必须在拆分前完成，防止同分异写泄漏。
- 不同不确定性方法必须单独校准，不能把 dropout、树间方差和 MVE 方差当成同一量。
- 只在查询后揭示 lookup 分数；全池分数仅用于最终 recovery 计算。

## 证据交付

```text
reproduction/runs/P06/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── data_sha256.txt
├── model_uncertainty_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

指纹缓存和大型池放外部存储，只在 source lock 中记录路径、大小和 SHA-256。

## 停止条件

- Smoke 成功：10k lookup 的 RF+Greedy/Random 均完成两轮，查询合法、无标签泄漏且输出可重跑。
- 立即阻塞：publication 环境不可解析且任何修复改变模型/采集语义、SMILES/分数错位、目标方向不明、外部数据许可不清。
- 只有论文指定数据规模、模型/策略、重复轨迹、作者分析脚本图、环境和偏差齐全后才可 `completed`；只完成 10k/50k 时写清范围。
