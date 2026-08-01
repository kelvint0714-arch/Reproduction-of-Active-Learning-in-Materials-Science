# W04｜ALEBREW 不确定性偏置分子动力学复现路径

> 状态：`recipe-ready`、`offline-only`。公开数据上的训练/评估可回放；从头生成论文
> 全部 DFT 标签与长时间 MD 需要外部量化计算资源。

## 定位与边界

- 论文：*Uncertainty-biased molecular dynamics for learning uniformly accurate
  interatomic potentials*，npj Computational Materials 10, 83 (2024)，
  DOI：<https://doi.org/10.1038/s41524-024-01254-1>。
- 分类：势函数主动学习/增强采样。模型不确定性既用于偏置 MD 探索，也用于停止、
  批量选择和校准；不是寻找材料最优配方的 BO。
- 最小复现：CPU 环境读取 Zenodo 的 alanine-dipeptide 数据，用默认配置完成缩短版
  训练与测试，验证模型、误差和不确定性输出。
- 忠实复现：按 Zenodo 中 `ala2-ffs` / `mil53` 各任务的 `config.yaml` 重跑论文比较。
- 从头 oracle 对 alanine 使用 FHI-aims、对 MIL-53 使用 CP2K；完整数据生成通常需
  GPU/HPC/DFT，标记 `offline-only`。

## 来源锁定

- 正式论文：Nature DOI 页面。
- 官方代码：<https://github.com/nec-research/alebrew>。
- 2026-07-31 核验 `main` commit：
  `3439211d2cd27be3f013d96f6ca4d062277627eb`。
- 固定数据：Zenodo v1，DOI <https://doi.org/10.5281/zenodo.10776838>；
  `ala2-ffs.zip` 146,129,485 bytes，MD5
  `c9d5bc06e12b0923457635f9323dc07d`；`mil53.zip` 559,281,684 bytes，MD5
  `306b7344c15a4f211b9b8d2784416081`。
- 代码为仓库 `LICENSE.txt` 的非商业许可；Zenodo 数据为 CC BY-NC 4.0。使用和
  再分发必须分别遵守。

```bash
git clone https://github.com/nec-research/alebrew.git \
  ../upstream/W04-alebrew
git -C ../upstream/W04-alebrew remote -v
git -C ../upstream/W04-alebrew branch --show-current
git -C ../upstream/W04-alebrew describe --tags --always --dirty
git -C ../upstream/W04-alebrew rev-parse HEAD
git -C ../upstream/W04-alebrew status --short
git -C ../upstream/W04-alebrew checkout \
  3439211d2cd27be3f013d96f6ca4d062277627eb
```

```bash
curl -L https://zenodo.org/api/records/10776838/files/ala2-ffs.zip/content \
  -o reproduction/runs/W04/raw_results/ala2-ffs.zip
md5 reproduction/runs/W04/raw_results/ala2-ffs.zip
shasum -a 256 reproduction/runs/W04/raw_results/ala2-ffs.zip \
  > reproduction/runs/W04/data_sha256.txt
```

只有需要 MIL-53 T2 时再下载 559 MB 归档。保存 Zenodo 元数据 JSON、Git SHA、
许可文本、文件大小、MD5 和本地 SHA-256 到 `source_lock.md`。

## 环境

环境名按上游文件使用 `alebrew-cpu`（或重命名副本
`al-w04-alebrew-cpu`）。优先使用 `alebrew-cpu.yml`、`alebrew-mps.yml` 或
`alebrew-cuda.yml`，不得凭猜测重写版本。

```bash
conda env create -f ../upstream/W04-alebrew/alebrew-cpu.yml
conda activate alebrew-cpu
export PYTHONPATH="$(pwd)/../upstream/W04-alebrew:$PYTHONPATH"
python -m pip check
python -m pip freeze > reproduction/runs/W04/pip-freeze.txt
conda env export --no-builds > reproduction/runs/W04/environment.yml
python - <<'PY' > reproduction/runs/W04/hardware.txt
import platform, torch
print(platform.platform())
print("torch", torch.__version__)
print("cuda", torch.cuda.is_available())
print("mps", hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
PY
```

上游 CPU 环境已明确 Python 3.10、PyTorch、BMDAL-REG、ASE 3.22.1。若求解器或
DFT 后端另建环境/容器，记录完整版本和许可证，不把可执行文件提交。

## T0｜来源和入口核验

```bash
conda activate alebrew-cpu
python -c "import alebrew, torch, ase; print(alebrew.__file__, torch.__version__, ase.__version__)"
python ../upstream/W04-alebrew/scripts/run_train.py --help || true
test -f ../upstream/W04-alebrew/config.yaml.default
```

解压 `ala2-ffs.zip` 到运行目录外，核对内部 `ala2_init.extxyz`、
`ala2_test.extxyz`、任务/方法配置文件和所有哈希。`--help` 若因 Fire CLI 行为返回
非零，记录实际输出，不把它误判为训练失败。

## T1｜最小离线回放

1. 从上游 `config.yaml.default` 复制到
   `reproduction/runs/W04/configs/config_smoke.yaml`。
2. 只修改数据/输出绝对路径，并将训练轮数缩短到能完成 smoke；保存与默认配置的
   diff 到 `deviations.md`。
3. 在独立工作目录运行：

```bash
python ../upstream/W04-alebrew/scripts/run_train.py \
  reproduction/runs/W04/configs/config_smoke.yaml \
  2>&1 | tee reproduction/runs/W04/logs/t1_train.log
python ../upstream/W04-alebrew/scripts/run_test.py \
  reproduction/runs/W04/configs/config_smoke.yaml \
  2>&1 | tee reproduction/runs/W04/logs/t1_test.log
```

成功标准：训练正常结束、模型文件产生、`test_results.json` 可解析，能量/力预测和
不确定性为有限值。缩短训练不与论文数值比较。

## T2｜忠实复现论文主结果

- 直接使用 Zenodo 各目录中的论文 `config.yaml`，分别重跑
  `ala2-{300,600,1200}K-ffs` 和选定 MIL-53 温压任务；不得从图中手抄参数。
- 对每个方法锁定 data/model/simulation/selection seed，保留初始数据与测试数据。
- 比较 unbiased MD、uncertainty-biased MD、adversarial 等论文实际配置；保存所有
  选择构型和不确定性校准参数。
- 先做公开标签离线回放；需要 FHI-aims/CP2K 重新标注时单独进入 HPC 层，记录输入、
  基组/赝势、SCF 收敛、作业资源与失败。
- 按论文图表核对能量/力误差分布、最坏区域误差、构型覆盖、校准和数据效率；不能
  只比较平均 RMSE。

## T3｜统一协议重实现或消融

- 同一初始集、oracle 预算、MD 步数和测试集比较 unbiased、uncertainty-biased、
  adversarial 与 Random frame。
- 消融 posterior/distance/ensemble 不确定性、conformal calibration、偏置强度、
  氢原子相对偏置和 batch diversity。
- 指标：能量 MAE/RMSE（每原子）、力 MAE/RMSE/max error、95% coverage、
  校准误差、构型空间覆盖、oracle 调用数和总成本。
- 训练/测试按独立轨迹或构象簇划分，避免相邻 MD 帧泄漏。
- 偏置策略不得读取测试误差；所有失败/非物理构型计入安全与稳定性指标。

## T4｜迁移到粘合剂 / DGEBA

- 直接价值在原子层：若研究环氧固化、金属界面或低温断裂，可用不确定性偏置 MD
  主动补充势函数构型；它不能直接预测配方表中的剪切强度。
- 前提是定义元素、反应路径、原子结构、量化标签和验证性质；现有 Excel 不满足。
- 可先借鉴“校准不确定性 + 多样性 batch selection”到表格 AL，与 Random/DAGS
  比较，再决定是否投入 DFT 势函数路线。
- 跨尺度使用时必须明确原子模拟输出如何成为配方级特征或约束，不能把势能误差直接
  解释为粘接强度。

## 公平性与评价

- 固定初始构型、MD 温压路径、步长、预算、seed、校准集和独立测试轨迹。
- 各策略使用相同 oracle 调用上限；同时报告误差、最坏误差、覆盖和计算成本。
- 相邻帧不能随机拆到训练和测试；MIL-53 不同温压/孔型应做域外留出。
- 采集不确定性必须在查询标签前计算；测试集只在评估时读取。
- 数据/代码均有非商业限制，交付物中保留 attribution 和许可边界。

## 证据交付

```text
reproduction/runs/W04/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── data_sha256.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

保存配置 diff、模型 seed、每轮/每帧不确定性、选择构型 ID、oracle 状态、误差与资源
曲线。受非商业许可约束的归档和完整上游仓库不提交。

## 停止条件

- T1 成功：固定源码/数据可读，缩短训练和独立测试结束，结果 JSON 无 NaN。
- 停止并标 `blocked`：Zenodo checksum 不符、许可证与预期用途冲突、环境文件无法
  解析、参考计算持续不收敛或生成非物理构型。
- 无 FHI-aims/CP2K/HPC 时保持 `offline-only`，公开标签回放仍可完成。
- 只有固定来源/环境/数据、完整配置与日志、全部主结果/基线/消融、逐图核对和偏差
  齐全，才可标 `completed`。
