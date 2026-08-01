# P09｜DP-GEN 并发学习复现路径

> 状态：`source-lock-needed`、`offline-only`。CLI/单元测试可在本地核验；论文级
> Deep Potential→MD→DFT 循环通常需要 GPU、HPC 和第一性原理后端。

## 定位与边界

- 论文：*DP-GEN: A concurrent learning platform for the generation of reliable
  deep learning based potential energy models*，Computer Physics Communications
  253, 107206 (2020)，DOI：<https://doi.org/10.1016/j.cpc.2020.107206>。
- 分类：并发学习/主动学习。多个 Deep Potential 模型的力预测分歧驱动构型选择；
  不是 GP+EI/UCB 的 BO。
- 最小复现：固定源码、安装 CLI，运行不需要真实后端的 generator 单元测试，检查
  训练/探索/标注三阶段任务能被正确生成。
- 忠实复现：用论文体系和阈值运行多模型训练、LAMMPS 探索、DFT 标注与回填。
- 完整工作需要 DeePMD-kit、带 DeePMD 接口的 LAMMPS、DFT 后端与调度系统；
  VASP 还需合法许可证。普通电脑只做 T0/T1，标记 `offline-only`。

## 来源锁定

- 正式论文：DOI 页面。
- 官方代码：<https://github.com/deepmodeling/dpgen>，LGPL-3.0。
- 官方文档：<https://docs.deepmodeling.com/projects/dpgen/>。
- 2026-07-31 核验当前 `master` 为
  `d5ce577fb91b9b6f3586748371ab1c231a586791`，可作为 API/smoke 基线。
- 论文没有在当前卡片中给出唯一 commit；忠实 T2 前必须从论文补充材料、发布历史
  和兼容的 DeePMD 版本解析“论文版本”，因此状态含 `source-lock-needed`。不得
  默认当前 master 等于 2020 论文代码。

```bash
git clone https://github.com/deepmodeling/dpgen.git \
  ../upstream/P09-dpgen
git -C ../upstream/P09-dpgen remote -v
git -C ../upstream/P09-dpgen branch --show-current
git -C ../upstream/P09-dpgen describe --tags --always --dirty
git -C ../upstream/P09-dpgen rev-parse HEAD
git -C ../upstream/P09-dpgen status --short
git -C ../upstream/P09-dpgen checkout \
  d5ce577fb91b9b6f3586748371ab1c231a586791
```

在 `source_lock.md` 分别记录：

1. “当前 API smoke commit”；
2. “论文忠实 commit/tag”（解析后补入）；
3. DeePMD-kit、LAMMPS、DFT 后端和 `dpdispatcher` 的版本/容器 digest；
4. 输入结构、赝势和初始标签数据的 SHA-256 与许可。

## 环境

环境名建议 `al-p09-dpgen-smoke`。当前仓库声明 Python `>=3.9`；优先安装锁定源码，
不手工猜测传递依赖版本。

```bash
conda create -n al-p09-dpgen-smoke python=3.10 pip -y
conda activate al-p09-dpgen-smoke
python -m pip install -e '../upstream/P09-dpgen[tests]'
python -m pip check
dpgen -h
python -m pip freeze > reproduction/runs/P09/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P09/environment.yml
```

T2 另建 `al-p09-dpgen-paper`，按解析出的历史 tag 和官方兼容矩阵安装
DeePMD/LAMMPS；不要污染 smoke 环境。记录 `nvidia-smi`、CPU/GPU、调度器、MPI、
DFT 可执行文件版本和容器 digest。密钥、许可证文件、POTCAR 不得提交。

## T0｜来源和入口核验

```bash
conda activate al-p09-dpgen-smoke
dpgen -h | tee reproduction/runs/P09/logs/t0_cli.log
python -c "import dpgen; print(dpgen.__file__)"
python -m pytest --collect-only ../upstream/P09-dpgen/tests/generator \
  > reproduction/runs/P09/logs/t0_tests_collected.log
```

检查官方 `examples/run/` 的 `param.json` 与 `machine.json`，但不要直接执行其中的旧
绝对路径或集群命令。

## T1｜最小离线回放

运行无需外部 DeePMD/LAMMPS/DFT 可执行文件的任务生成与筛选单元测试：

```bash
python -m pytest -q \
  ../upstream/P09-dpgen/tests/generator/test_make_train.py \
  ../upstream/P09-dpgen/tests/generator/test_make_md.py \
  ../upstream/P09-dpgen/tests/generator/test_make_fp.py \
  ../upstream/P09-dpgen/tests/generator/test_post_fp.py \
  2>&1 | tee reproduction/runs/P09/logs/t1_generator_tests.log
```

另复制一份最新官方示例到 `configs/`，只做 schema/路径审计，不提交任务。成功标准：
测试通过；能识别 `00.train`、`01.model_devi`、`02.fp` 阶段；候选由 force model
deviation 的低/高阈值区间筛出。T1 不等于训练出势函数。

## T2｜忠实复现论文主结果

1. 先完成论文版本锁定；保存论文体系初始构型、DFT 设置、训练网络、模型数、探索
   温压路径和 `model_devi_f_trust_lo/hi`。
2. 用多个不同随机种子训练 Deep Potential committee；模型不得共享随机初始化。
3. 用论文一致的 LAMMPS/MD 探索，逐帧保存最大力分歧，将构型分为 accurate、
   candidate 和 failed。
4. 只对 candidate 调用锁定的 DFT 设置；回填能量、力、应力后开始下一轮。
5. 保存每轮候选比例、DFT 调用数、能量/力误差、构型覆盖与总 GPU/CPU/DFT 成本。
6. 用独立构型/相区测试集逐图核对论文主结果；训练探索轨迹不能兼作测试集。
7. 若所需 VASP/POTCAR 或论文输入不公开，T2 必须停在相应层并明确 `blocked`，不可
   用别的 DFT 标签冒充忠实结果。

## T3｜统一协议重实现或消融

- 在同一初始数据、MD 轨迹和预算下比较 Random frame、固定间隔 frame、committee
  disagreement；统一 DFT 标签上限。
- 消融 committee 大小、低/高分歧阈值、温度计划和每轮最大标注数。
- 指标：独立测试能量 MAE/RMSE（每原子）、力分量 MAE/RMSE、virial/stress
  误差、candidate/failed 比例、DFT 调用数、模型分歧—真实误差校准和总成本。
- 阈值只能由训练/验证体系确定；不得看最终测试误差后调阈值。
- 报告 seed 间方差与失败构型，不得删除“高分歧且 DFT 失败”的样本来美化结果。

## T4｜迁移到粘合剂 / DGEBA

- DP-GEN 接受原子构型、能量、力和应力，不接受配方 Excel；不能直接套到当前表格。
- 可迁移思想是“模型 committee 分歧→查询真实 oracle”。表格任务可用 RF/XGBoost/
  NN ensemble 的预测分歧选下一配方，而无需安装 DP-GEN。
- 只有研究固化反应、界面或低温原子模拟并拥有可靠 DFT/MD 标签时，才考虑 DP-GEN
  构建势函数；这与宏观剪切强度预测是两个层次。
- 建立跨尺度联系前必须定义原子模拟输出怎样进入配方特征或物理模型，不能直接把
  势函数误差当胶黏剂性能。

## 公平性与评价

- 固定初始构型、committee seed、MD 条件、分歧阈值、每轮/总 DFT 预算和独立测试集。
- Random/固定间隔基线必须使用同样 DFT 调用数和同一测试集。
- 结构泄漏：同一 MD 邻近帧高度相关，训练/测试按轨迹、温压或相区分组。
- 时间泄漏：后续轮次发现的构型不能进入早期模型或早期阈值校准。
- 势函数指标必须含能量、力及稳定性；仅报告训练 loss 不足。

## 证据交付

```text
reproduction/runs/P09/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

另保存每轮 `param.json`/`machine.json`、模型 seed、候选清单、DFT 状态与作业 ID、
资源用量和失败日志。不得提交 POTCAR、集群凭据、完整上游仓库或无再分发许可数据。

## 停止条件

- T1 成功：锁定 commit 的 CLI 可用，四类 generator 测试通过，三阶段输入输出可解释。
- 停止并标 `blocked`：论文 commit/输入无法解析、所需 DFT 许可证/赝势不可取得、
  后端版本不兼容、候选筛选含非有限值或集群连续失败。
- 缺 HPC/DFT 时保持 `offline-only`，不将单元测试写成论文复现。
- 只有论文来源版本、全后端环境、完整循环日志、独立测试、基线/消融、逐图核对和
  所有偏差齐全，才可标 `completed`。
