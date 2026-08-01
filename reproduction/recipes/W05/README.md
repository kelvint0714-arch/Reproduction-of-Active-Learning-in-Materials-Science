# W05｜FLARE 在线贝叶斯力场复现路径

> 状态：`source-lock-needed`、`offline-only`。公开轨迹与 GP/SGP 代码可离线回放；
> 论文全部在线 DFT/长时间稀有事件需要 HPC 和第一性原理后端。

## 定位与边界

- 论文：*On-the-fly active learning of interpretable Bayesian force fields for
  atomistic rare events*，npj Computational Materials 6, 20 (2020)，
  DOI：<https://doi.org/10.1038/s41524-020-0283-z>。
- 分类：GP/稀疏 GP 力场的在线主动学习。每个力分量的认知不确定性超过噪声阈值时
  调 DFT，并加入最高不确定局部环境；不是 BO。
- 最小复现：固定当前 FLARE 源码，运行 GP/SGP 单元测试，解析公开/测试 OTF 轨迹并
  检查“不确定性阈值→DFT frame→模型更新”记录。
- 忠实复现：锁定论文时代 FLARE 版本与 Materials Cloud 数据，重放铝熔化、空位/
  吸附原子等实验并核对论文图。
- 从头 DFT/1 ns 稀有事件通常需 HPC；VASP/量化后端另有许可，标 `offline-only`。

## 来源锁定

- 正式论文：Nature DOI 页面。
- 官方代码：<https://github.com/mir-group/flare>，MIT。
- 论文归档数据：Materials Cloud
  <https://doi.org/10.24435/materialscloud:2020.0017/v1>。
- 2026-07-31 核验当前 `master` 为
  `3fd04311a0908d9fcd0cc9da284f2cd7ef459499`，仅作为现代 smoke 基线。
- 论文未在当前卡片中指定唯一 Git commit；T2 前须从归档/论文补充材料解析历史
  版本，不能用 2026 年 FLARE 1.4.3 冒充 2020 论文实现。

```bash
git clone https://github.com/mir-group/flare.git \
  ../upstream/W05-flare
git -C ../upstream/W05-flare remote -v
git -C ../upstream/W05-flare branch --show-current
git -C ../upstream/W05-flare describe --tags --always --dirty
git -C ../upstream/W05-flare rev-parse HEAD
git -C ../upstream/W05-flare status --short
git -C ../upstream/W05-flare checkout \
  3fd04311a0908d9fcd0cc9da284f2cd7ef459499
```

从 Materials Cloud DOI 页面下载文件时保存归档页面、文件名、大小、平台 checksum
与本地 SHA-256：

```bash
find reproduction/runs/W05/raw_results/materialscloud -type f -print0 |
  sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/W05/data_sha256.txt
```

在 `source_lock.md` 明确区分“现代 smoke commit”和“论文忠实 commit/tag”，并保存
代码/数据许可。若平台未提供许可，禁止再分发，保留本地路径和哈希即可。

## 环境

现代 smoke 环境名 `al-w05-flare-smoke`。优先使用锁定源码的 `pyproject.toml`；
其声明 Python `>=3.7`，但不要因此猜论文时代依赖。

```bash
conda create -n al-w05-flare-smoke python=3.10 pip compilers cmake -y
conda activate al-w05-flare-smoke
python -m pip install -e '../upstream/W05-flare[tests]'
python -m pip check
python -m pip freeze > reproduction/runs/W05/pip-freeze.txt
conda env export --no-builds > reproduction/runs/W05/environment.yml
python - <<'PY' > reproduction/runs/W05/hardware.txt
import platform, flare
print(platform.platform())
print(flare.__file__)
PY
```

T2 单独创建论文兼容环境，并记录 C/C++ 编译器、BLAS/MKL、ASE、LAMMPS、MPI 和
DFT 后端。官方 README 说明大模型可能需要 100 GB 以上内存；不要在笔记本上直接
启动全量任务。

## T0｜来源和入口核验

```bash
conda activate al-w05-flare-smoke
python -c "import flare; print(flare.__file__)"
flare-otf --help | tee reproduction/runs/W05/logs/t0_cli.log
python -m pytest --collect-only ../upstream/W05-flare/tests \
  > reproduction/runs/W05/logs/t0_tests_collected.log
```

检查 `examples/test_SGP_Fake_fresh.yaml`、`tests/test_files/sic_dft.xyz` 和归档数据
均可读。记录是否有可用 `lmp`；没有时不要把被 skip 的 OTF 测试写成通过。

## T1｜最小离线回放

先运行不依赖外部 DFT 的 GP/SGP 核心测试：

```bash
python -m pytest -q \
  ../upstream/W05-flare/tests/test_gp.py \
  ../upstream/W05-flare/tests/test_sparse_gp.py \
  ../upstream/W05-flare/tests/test_parse_otf.py \
  2>&1 | tee reproduction/runs/W05/logs/t1_core.log
```

若已安装兼容 LAMMPS 并设置 `lmp`，再在临时工作目录运行 fake OTF：

```bash
export lmp=/absolute/path/to/lammps
cd ../upstream/W05-flare/tests
python -m pytest -q test_fake_otf.py \
  2>&1 | tee "$OLDPWD/reproduction/runs/W05/logs/t1_fake_otf.log"
```

成功标准：GP/SGP 预测与序列化测试通过；若跑 fake OTF，轨迹的 DFT frames、训练
环境和重启可解析。被 `skip` 不算 OTF smoke 成功，必须如实记录。

## T2｜忠实复现论文主结果

1. 解析并锁定 2020 论文代码/环境；用 Materials Cloud 固定归档作为首选数据源。
2. 回放铝固态→液态轨迹，保存温度、每次 DFT 调用、噪声不确定性和加入的环境。
3. 在论文独立 solid/liquid AIMD 测试结构上重算 force RMSE；与 EAM、AGNI 和
   2-body/2+3-body FLARE 的定义保持一致。
4. 回放 vacancy/adatom 稀有事件、迁移路径能量/力及不确定性；公开数据不足的环节
   标“不可重建”，不插值伪造。
5. 从头在线 DFT 层单独提交 HPC：锁定结构、温度计划、阈值倍数、每次加入环境数、
   DFT 设置、核数和墙钟时间。
6. 按论文 Fig. 3/4/6 与 Table 1 逐项核对；论文报告的计算加速只能用同硬件/定义
   重算或标为不可直接比较。

## T3｜统一协议重实现或消融

- 相同初始结构、MD 路径和 DFT 上限下比较 Random/fixed interval、2-body GP、
  2+3-body GP 和 sparse GP。
- 消融不确定性阈值倍数、噪声优化、每次加入局部环境数和映射 GP。
- 指标：独立测试 force RMSE/95th percentile、energy error、coverage、DFT 调用数、
  稳定 MD 时间、稀有事件覆盖与 s/atom/timestep。
- 相邻 AIMD 帧按轨迹/时间 block 留出，避免同轨迹泄漏。
- 不确定性阈值必须在测试前固定；DFT 失败和数值爆炸纳入失败率。

## T4｜迁移到粘合剂 / DGEBA

- FLARE 的直接对象是原子构型和力，不是配方表。只有在研究固化反应、金属界面、
  低温裂纹等原子过程时才直接适用。
- 表格 AL 可借鉴“预测不确定性超过阈值才做昂贵实验”，但代理模型和标签改为
  RF/GP/NN 与真实剪切强度，不需要 FLARE 代码。
- 若以后建立环氧/铝界面力场，需单独定义 DFT 数据、元素覆盖、反应性和验证基准；
  势函数误差不能直接等同宏观粘接性能。

## 公平性与评价

- 固定初始结构、温度计划、MD 步长、阈值、oracle 预算、seed 和测试轨迹。
- Random/定间隔基线使用相同 DFT 次数；同时报平均/尾部误差和成本。
- 训练与测试按轨迹、相态或缺陷类型分组；禁止相邻帧泄漏。
- 所有采集决策只能访问当前模型不确定性，不能读取未来 DFT 标签。
- 现代版与论文版结果分栏，API/算法漂移不可混合。

## 证据交付

```text
reproduction/runs/W05/
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

保存每 MD step 不确定性、DFT frame、加入环境、GP 超参数、独立测试预测、作业资源和
失败。VASP/POTCAR/凭据及无再分发许可的归档不提交。

## 停止条件

- T1 成功：核心 GP/SGP/解析测试通过；若声称 OTF smoke，则 fake OTF 未被 skip
  且阈值触发/回填/重启证据齐全。
- 停止并标 `blocked`：论文版本无法锁定、归档校验失败、编译/API 不兼容、DFT
  许可证缺失或长期在线运行不稳定。
- 缺 DFT/HPC 时保持 `offline-only`，不影响公开轨迹回放。
- 只有论文版本、环境、完整离线/在线日志、独立测试、基线/消融、逐图核对和偏差
  齐全，才可标 `completed`。
