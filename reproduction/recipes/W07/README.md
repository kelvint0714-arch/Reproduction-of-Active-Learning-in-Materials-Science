# W07｜FALCON 在线势函数主动学习复现路径

> 状态：`recipe-ready`、`offline-only`。EMT 教程可在 CPU 上直接闭环；论文中的
> VASP/长时间 MD 任务需要合法第一性原理后端和较大计算资源。

## 定位与边界

- 论文：*FALCON: fast active learning for machine learning potentials in
  atomistic and ab initio molecular dynamics simulations*，npj Computational
  Materials 12, 1 (2026；2025-12-12 在线发表)，
  DOI：<https://doi.org/10.1038/s41524-025-01897-8>。
- 分类：on-the-fly 主动学习势函数。代理不确定性超过阈值时调用精确 calculator；
  FALCON 通过聚类把训练结构分配给多个较小模型以降低频繁重训成本。
- 最小复现：官方 `simple_tutorial.py` 用 ASE EMT 充当精确 oracle，Pt₅₅ 上跑
  100 步，完全不需要 DFT。
- 忠实复现：运行 paper 目录的 Pt/聚类、Al、CNT/H₂O 等脚本并逐图比较。
- Al/CNT 脚本使用 VASP；Pt 的百万步和聚类比较也耗时。分层执行，真实 DFT/HPC
  部分标 `offline-only`。

## 来源锁定

- 正式论文：Nature DOI 页面。
- 官方代码：<https://github.com/thequantumchemist/falcon>，GPL-3.0。
- 固定 release：tag `v1.3`，peeled commit
  `9e12442ae445434765a2a367d5cc3ceb456c35fc`；仓库 `setup.py` 版本 1.3.0。
- `paper/` 包含论文输入，`falcon_md/tutorial/` 包含 EMT smoke 教程。

```bash
git clone --branch v1.3 --single-branch \
  https://github.com/thequantumchemist/falcon.git \
  ../upstream/W07-falcon
git -C ../upstream/W07-falcon remote -v
git -C ../upstream/W07-falcon branch --show-current
git -C ../upstream/W07-falcon describe --tags --always --dirty
git -C ../upstream/W07-falcon rev-parse HEAD
git -C ../upstream/W07-falcon status --short
test "$(git -C ../upstream/W07-falcon rev-parse HEAD)" = \
  "9e12442ae445434765a2a367d5cc3ceb456c35fc"
```

将 tag/SHA、GPL 文本、paper/tutorial 文件 SHA-256 和访问日期写入
`reproduction/runs/W07/source_lock.md`：

```bash
find ../upstream/W07-falcon/paper ../upstream/W07-falcon/falcon_md/tutorial \
  -type f -print0 | sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/W07/source_files_sha256.txt
```

## 环境

环境名建议 `al-w07-falcon-v13`。上游 `setup.py` 声明 Python `>=3.8` 及
`agox`、`numpy`、`ase`、`pytest`，优先从锁定源码安装，不另猜版本。

```bash
conda create -n al-w07-falcon-v13 python=3.10 pip -y
conda activate al-w07-falcon-v13
python -m pip install -e ../upstream/W07-falcon
python -m pip check
python -m pip freeze > reproduction/runs/W07/pip-freeze.txt
conda env export --no-builds > reproduction/runs/W07/environment.yml
python - <<'PY' > reproduction/runs/W07/hardware.txt
import platform, ase, falcon_md
print(platform.platform())
print("ase", ase.__version__)
print(falcon_md.__file__)
PY
```

VASP 层另记录 VASP、赝势、MPI、ASE calculator、CPU/HPC 和许可证；不得提交
POTCAR、许可证文件或集群凭据。

## T0｜来源和入口核验

```bash
conda activate al-w07-falcon-v13
python -c "from falcon_md.otf_calculator import FALCON; from falcon_md.models.agox_models import GPR; print('imports ok')"
python -m compileall -q ../upstream/W07-falcon/falcon_md
test -f ../upstream/W07-falcon/falcon_md/tutorial/simple_tutorial.py
test -f ../upstream/W07-falcon/paper/pt_input.py
```

记录 AGOX/ASE 实际解析版本，确认 `Pt55` 结构可加载、EMT 能给出能量/力。

## T1｜最小离线回放

在运行目录复制官方脚本，保持参数不变（100 MD 步）：

```bash
mkdir -p reproduction/runs/W07/raw_results/simple
cd reproduction/runs/W07/raw_results/simple
python ../../../../../../upstream/W07-falcon/falcon_md/tutorial/simple_tutorial.py \
  2>&1 | tee ../../logs/t1_simple.log
```

若相对路径不同，使用已记录的绝对上游路径，不改算法。成功标准：

- `opt.traj` 和 `MD.traj` 存在并可由 ASE 读取；
- 至少一次 GPR 训练完成；
- 日志可辨认是否/何时不确定性超过 `accuracy_e=0.10 eV` 并调用 EMT；
- MD 轨迹 100 步无 NaN/爆炸。

若阈值下恰好未触发新增 oracle 调用，T1 只能证明教程运行；需在 T3 另用较低阈值
做“触发测试”，并记录偏差。

## T2｜忠实复现论文主结果

分三层，不能跳过资源声明：

1. **CPU/EMT 层**：运行 `paper/pt_input.py` 的 Pt13/55/147/561 与不同温度/阈值；
   按论文原 1,000,000 MD 步。运行 `pt_clustering_input.py` 的 modelsize
   100/200/500 对照，保持总训练结构/步数一致。
2. **HPC/VASP 层（offline-only）**：用 `paper/al_input.py` 的 Al PBE 设置和
   `accuracy_e=0.05/0.10 eV`；用 `paper/cnt_input.py` 的 CNT/H₂O 设置。保存
   每次 VASP 输入、输出、收敛和资源。
3. **逐图核对**：训练时间随数据量/cluster 数、精确调用次数、能量/力不确定性、
   MD 能量/结构稳定性和不同体系表现。论文脚本给出的参数是入口，但仍须与正文/
   补充材料逐项核对。

输出放在每个 run 独立目录，禁止多个脚本覆盖同名 `MD.traj`、`opt.traj`。

## T3｜统一协议重实现或消融

- 相同 Pt55 初始结构、EMT oracle、seed、温度、步数和阈值下比较：无 clustering、
  modelsize 100/200/500、不同 max_clusters。
- 消融 `accuracy_e`、force threshold、`train_start`、`train_every`、指数训练日志和
  SparseGPR/GPR；每次只改一个因素。
- 加入“较低阈值的 100-step trigger smoke”，验证确实发生
  uncertainty→oracle→retrain。
- 指标：oracle 调用数、训练次数/墙钟时间、每步预测成本、energy/force MAE、
  不确定性校准、cluster 大小/负载和 MD 稳定步数。
- 用相同硬件和线程比较运行时；初始化/轨迹 seed 固定，多 seed 报方差。

## T4｜迁移到粘合剂 / DGEBA

- FALCON 直接适用于原子级固化/界面 MD，不适用于当前配方 Excel。
- 可迁移思想是“训练数据增大时聚类成局部小模型”和“不确定性超过阈值才查询昂贵
  oracle”；表格任务可用 mixture-of-experts/局部 GP 做独立研究。
- 当前小样本先用单一 GP/RF/DAGS；只有证据显示数据跨多个化学域且全局模型重训
  成为瓶颈，再引入 FALCON 式聚类，避免过度工程。
- 若进入原子模拟，必须另建结构、DFT、势函数和宏观性能连接方案。

## 公平性与评价

- 固定初始结构、速度 seed、温度计划、步数、精度阈值、oracle 和硬件。
- clustering 与单模型使用相同 oracle 标签和总 MD 步；运行时比较包含聚类开销。
- 训练轨迹和独立验证轨迹分开；相邻帧不能随机拆分。
- 精确 calculator 的调用与失败全部计数；不得缓存一方而不给另一方相同条件。
- EMT 结果只证明软件闭环，不等于 DFT 精度。

## 证据交付

```text
reproduction/runs/W07/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── source_files_sha256.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

每个 run 保存脚本副本/哈希、trajectory、训练数据、模型/cluster 状态、oracle 调用、
时间/内存和失败。VASP 专有文件不提交。

## 停止条件

- T1 成功：v1.3 安装完成、Pt55 EMT 教程 100 步无异常、轨迹与训练日志可审计。
- 停止并标 `blocked`：tag/commit 不符、AGOX API 与 v1.3 不兼容且无法审计修复、
  轨迹出现非有限值、VASP 许可证/赝势缺失或长任务持续不收敛。
- 无 VASP/HPC 时保持 `offline-only`，CPU/EMT 结果单独完成。
- 只有固定来源/环境、完整论文层结果、基线/消融、逐图核对、资源和偏差证据齐全，
  才可标 `completed`。
