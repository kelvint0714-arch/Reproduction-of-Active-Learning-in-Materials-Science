# S02｜PiNDiff-CVI 概率物理融合神经微分模型复现

**路径状态**：`recipe-ready`（首次执行仍需把上游 `main` 解析为 commit SHA）
**论文**：[Probabilistic physics-integrated neural differentiable modeling for isothermal chemical vapor infiltration process](https://doi.org/10.1038/s41524-024-01307-5)
**正式论文卡**：[`papers/supporting/physics_modeling/S02_PiNDiff_CVI.md`](../../../papers/supporting/physics_modeling/S02_PiNDiff_CVI.md)

## 定位与边界

PiNDiff 保留 CVI 演化方程结构，用神经网络学习未知扩散、反应和有效表面积算子，并用深度集成表达不确定性。它是**概率物理代理模型**，原论文没有采集函数/回填循环，不是主动学习。

- 最小复现：官方 synthetic 数据生成＋一个成员短训练/测试。
- 忠实复现：按官方 YAML 运行 synthetic 与 Benzinger 实验案例、多个 ensemble 成员和论文后处理。
- 官方环境锁定 Linux/NVIDIA CUDA 11/cuDNN 8.2 的 JAX；Apple Silicon 不能原样忠实运行。
- 普通 CPU 可做偏差明确的 smoke；论文训练建议 Linux GPU。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1038/s41524-024-01307-5`
- 作者仓库：[jx-wang-s-group/PiNDiff-CVI](https://github.com/jx-wang-s-group/PiNDiff-CVI)，Apache-2.0
- 官方入口：`main.py`、`input/case_setup*.yaml`、`Postprocessing.ipynb`
- 上游无 tag/release；必须锁 `main` SHA。

```bash
git clone https://github.com/jx-wang-s-group/PiNDiff-CVI.git \
  ../upstream/S02-pindiff-cvi
git -C ../upstream/S02-pindiff-cvi remote -v
git -C ../upstream/S02-pindiff-cvi branch --show-current
git -C ../upstream/S02-pindiff-cvi describe --tags --always --dirty
git -C ../upstream/S02-pindiff-cvi rev-parse HEAD
git -C ../upstream/S02-pindiff-cvi status --short
shasum -a 256 ../upstream/S02-pindiff-cvi/LICENSE \
  ../upstream/S02-pindiff-cvi/environment.yml
find ../upstream/S02-pindiff-cvi/input -type f \
  -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/S02/data_sha256.txt
```

写入 `reproduction/runs/S02/source_lock.md`；实验数据的原始引用和再分发权仍须从论文核对。

## 环境

环境名采用上游 `jax1`。官方 `environment.yml` 指定 Python 3.10.6、JAX 0.3.23、`jaxlib 0.3.22+cuda11.cudnn82`、Haiku/Optax 等，优先在 Linux NVIDIA 容器/HPC 原样建立：

```bash
conda env create -f ../upstream/S02-pindiff-cvi/environment.yml
conda activate jax1
python -m pip check
python -m pip freeze > reproduction/runs/S02/pip-freeze.txt
conda env export --no-builds > reproduction/runs/S02/environment.yml
nvidia-smi > reproduction/runs/S02/nvidia-smi.txt
```

CPU smoke 可复制 YAML 并仅把 CUDA jaxlib 改为对应 CPU wheel，保存 `environment-cpu.yml` 和 patch；该结果不是 T2 忠实性能环境。不要直接升级到现代 JAX 后忽略数值/API 变化。

## T0｜来源、配置和物理量核验

1. 固定 commit、环境、所有 input/实验数据哈希。
2. 从论文建立已知方程—未知 NN 算子—代码类映射：`Diff_NN`、`Krxn_NN`、`S2Vc_NN` 等。
3. 审计 `input/case_setup.yaml`、Benzinger2/3 和 Wei 配置，记录温度、压力、网格、时间、训练/测试、seed 和输出路径。
4. 确认 `gen_syn_data`、`load_syn_data`、`ExpData_name`、`train_model` 四个开关的官方组合。
5. 建立论文图—`Postprocessing.ipynb`/plot Notebook—原始输出映射。

## T1｜最小 smoke test

在运行副本中保存原 YAML，再创建 `configs/smoke.yaml`：缩小网格/迭代、`gen_syn_data: True`、`train_model: False`，运行数值 synthetic 生成：

```bash
cd ../upstream/S02-pindiff-cvi
python main.py
```

随后设置 `gen_syn_data: False`、`load_syn_data: True`、`train_model: True`，只训练一个短成员。所有 YAML diff 和 stdout 复制到 `reproduction/runs/S02/`。Smoke 成功要求：synthetic 文件生成、状态量有限/物理范围正确、一次 forward/backward 完成且 checkpoint 可载入。

## T2｜忠实复现论文主结果

1. 在原 GPU 环境恢复论文 YAML、网格、epoch、ensemble 成员和种子。
2. 先生成/训练/测试 synthetic 案例，再运行 `ExpData_name: Benzinger2` 和 `Benzinger3`。
3. 保存每个 ensemble 成员的 checkpoint、状态预测、未知算子、孔隙率和耗时。
4. 在未见温度/压力条件上评估，并用 ensemble 均值/方差生成区间。
5. 执行官方后处理 Notebook，重画论文状态场、孔隙率、未知物理量和不确定性图。
6. 逐图/表核对，不能用一个 ensemble 成员代替概率结果。

## T3｜统一协议与消融

- 完整 PiNDiff、无未知算子 NN、纯数据 NN、确定性单模型、不同 ensemble size 比较。
- 对训练温度/压力覆盖、噪声、数据量和网格分辨率做消融。
- 评估已知物理守恒残差、未知算子恢复误差、外推误差和区间校准。
- 固定 seed 列表和数据 split；报告均值、方差与失败成员。
- CPU 与 GPU 的数值偏差单独记录，不混合性能时间。

## T4｜迁移到 DGEBA/粘合剂数据

只有在能写出固化/传热演化方程并指出未知算子时才迁移。可将 PiNDiff 作为固化过程代理和不确定性提供者，再由 UCB/EI 选择新工艺；这属于新增主动学习包装层，不是原论文结论。

迁移前需要时间/空间分辨的温度、固化度或热流数据，单一最终剪切强度表不足以辨识 PDE 中未知算子。与普通 GP/RF 和经典 PINN 做基线，避免为了“物理”强行套用。

## 公平性与评价

- 状态/算子：relative \(L_2\)、RMSE、最大误差，按变量和工况分别报告。
- 概率：NLL、95% coverage、区间宽度、ECE/校准曲线；ensemble 方差不能只画不评。
- 物理：守恒/演化残差和边界误差。
- 所有模型共享训练/验证/外推工况、网格、数据量和 seed。
- 标准化只在训练工况拟合；实验/未来工况不得参与调参。
- 原论文无 AL/BO 指标；T4 扩展才报告 regret/采集效率。

## 证据交付

```text
reproduction/runs/S02/
├── README.md
├── source_lock.md
├── environment.yml
├── environment-cpu.yml
├── pip-freeze.txt
├── nvidia-smi.txt
├── data_sha256.txt
├── physics_code_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

## 停止条件

- Smoke 成功：synthetic 数据可生成，一个短训练成员可保存/载入且状态量有限。
- 立即阻塞：原 JAX/CUDA 环境无法建立、配置单位/物理量不明、实验数据权利不清、升级依赖改变求解器。
- 只有 synthetic＋实验案例、完整 ensemble、外推/不确定性、官方图、环境和偏差齐全才可 `completed`。
