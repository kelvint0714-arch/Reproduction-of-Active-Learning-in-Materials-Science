# S03｜深共熔溶剂监督学习与 CGAN 候选生成复现

**路径状态**：`recipe-ready`（路径可审计；忠实论文数值复现仍因缺数据/环境/许可证而阻塞）
**论文**：[Machine learning models accelerate deep eutectic solvent discovery for the recycling of lithium-ion battery cathodes](https://doi.org/10.1039/D4GC01418A)
**正式论文卡**：[`papers/supporting/general_ml/S03_DES_ML.md`](../../../papers/supporting/general_ml/S03_DES_ML.md)

## 定位与边界

论文以 XGBoost/RF/SVR/ANN 预测 DES 浸出性能，用 SHAP 解释，再用 CGAN 生成理想描述符并通过相似度搜索得到候选。它是**监督学习＋生成/筛选**，没有按轮查询—回填—重训的主动学习循环。

- 最小 smoke：对作者代码做静态审计，并用明确 toy 数据验证单个模型/CGAN tensor 维度。
- 忠实复现：需要论文原始 CSV、描述符、划分、训练模型/超参和实验候选，目前官方仓库未提供。
- 已核验仓库只有源码和论文 PDF，缺数据、环境、运行脚本顺序和明确许可证；因此忠实复现阻塞。
- CGAN 训练建议 GPU；真实候选验证需要化学实验。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1039/D4GC01418A`
- 作者仓库：[wenbomu/ML-accelerate-deep-eutectic-solvent-discovery](https://github.com/wenbomu/ML-accelerate-deep-eutectic-solvent-discovery)
- 上游无 tag/release；GitHub 页面未给出独立许可证文件。
- 仓库包含一份论文 PDF，不能因此推定代码/数据许可，也不要复制进本仓库。

```bash
git clone https://github.com/wenbomu/ML-accelerate-deep-eutectic-solvent-discovery.git \
  ../upstream/S03-des-ml
git -C ../upstream/S03-des-ml remote -v
git -C ../upstream/S03-des-ml branch --show-current
git -C ../upstream/S03-des-ml describe --tags --always --dirty
git -C ../upstream/S03-des-ml rev-parse HEAD
git -C ../upstream/S03-des-ml status --short
find ../upstream/S03-des-ml -maxdepth 1 -type f \
  -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/S03/source_files_sha256.txt
```

将 commit、文件清单、无数据/环境/许可证的证据和联系作者请求写入 `reproduction/runs/S03/source_lock.md`。取得作者数据前不得上传或编造替代 CSV。

## 环境

上游未提供环境。已核验 import 涉及 PyTorch/torchvision、RDKit、scikit-learn、XGBoost、Pandas/NumPy/joblib。下面只用于隔离 smoke，不是作者环境：

```bash
conda create -n repro-s03-des-ml python=3.10 pip -y
conda activate repro-s03-des-ml
conda install -c conda-forge rdkit -y
python -m pip install numpy pandas scikit-learn xgboost torch torchvision joblib
python -m pip check
python -m pip freeze > reproduction/runs/S03/pip-freeze-smoke.txt
conda env export --no-builds > reproduction/runs/S03/environment-smoke.yml
```

Python 3.10 和依赖版本是本项目兼容性选择。只有取得作者环境/运行证据后才建立 `environment.yml`；不要猜 SHAP 版本或训练 CUDA。

## T0｜代码、数据缺口与论文协议核验

1. 固定仓库 SHA，审计 `data_process.py`、`train_test.py`、`model.py`、`filter.py`/`predicate.py`、`cgan.py`、`test.py`、`fun.py`。
2. 列出所有硬编码路径、预期文件名、列名、tensor shape、模型文件和输出。
3. 从论文/补充材料提取 HBA/HBD、比例、描述符、Morgan 指纹、目标、划分和指标；未知项标 `NR`。
4. 记录仓库缺失的 CSV/checkpoint/环境/许可证，向作者请求数据与运行顺序。
5. 明确 SHAP 在论文中的入口；若仓库没有对应脚本，不把自行生成的 SHAP 图当作者复现。

## T1｜最小 smoke test

只允许使用公开 toy 分子/随机数，并显著标记 `TOY / NOT PAPER DATA`：

1. 用少量公开 SMILES 测试 RDKit 指纹、HBA/HBD 配对和相似度函数。
2. 用小矩阵测试 SVR/RF/XGBoost/ANN 的 fit/predict 和输出维度。
3. 用极小 epoch 测试 CGAN forward/backward、条件维度和 checkpoint。
4. 运行 `python -m compileall` 和 import smoke，记录硬编码路径失败。

Smoke 成功只说明代码构件可运行，不允许计算“论文复现 R²”。

## T2｜忠实复现论文主结果

本阶段当前**阻塞**。只有取得合法原始数据和协议后：

1. 固定数据/模型/环境哈希，复现作者 train/test split 与描述符处理。
2. 在相同划分运行 SVR、RF、ANN、XGBoost，核对论文回归指标。
3. 复现论文 SHAP 输入/背景样本和特征排序。
4. 复现 CGAN 条件、训练轮次、生成描述符、相似度映射和实验候选。
5. 核对候选实验结果与论文表/图；不得用论文最终结果反向筛选生成样本。

若作者拒绝/无法提供数据，T2 永久标 blocked。

## T3｜统一协议与可审计重实现

在另有合法公开 DES 数据时，可以进行独立重实现：

- 按 HBA、HBD 或成对组合 group split，避免同分子近邻泄漏。
- Random/RF/XGBoost/SVR/ANN 共享 split 和调参预算。
- CGAN 与简单随机/插值/自编码器生成基线比较。
- 报告预测 MAE/RMSE/\(R^2\)、生成 validity/novelty/uniqueness/diversity、检索命中和实验 hit rate。
- SHAP 跨 seed/折稳定性单独评价。

所有结果标“新数据重实现”，不称论文数值复现。

## T4｜迁移到 DGEBA/粘合剂数据

S03 可提供监督模型、解释和候选生成参考，但不自带主动学习。当前数据可先用 RF/XGBoost＋SHAP；生成模型只有在真实样本显著增加、化学约束可验证时再考虑。

若生成新离子液体/多酚或配比，必须经过结构有效性、可获得性、安全、相容性和化学组审批，再进入主动学习候选池。CGAN 建议不能直接作为实验指令。Synthetic 标签只用于流程测试。

## 公平性与评价

- 监督：分组/nested CV 的 MAE、RMSE、\(R^2\)，报告 seed 分布。
- 生成：validity、uniqueness、novelty、diversity、约束满足率和最近邻相似度。
- 实验：候选 hit rate、改进幅度及重复误差；没有实验不得称发现。
- HBA/HBD、同分异写、Morgan 近邻必须防泄漏；Scaler 只拟合训练集。
- 模型/生成器调参预算一致，Random/简单生成基线不可省略。
- 本论文不是 AL，不能使用 regret/查询效率冒充原文主指标。

## 证据交付

```text
reproduction/runs/S03/
├── README.md
├── source_lock.md
├── environment-smoke.yml
├── pip-freeze-smoke.txt
├── source_files_sha256.txt
├── missing_assets.md
├── code_data_map.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

## 停止条件

- Smoke 成功：源码可编译，toy 指纹/模型/CGAN 各完成最小前后向且输出明确标 toy。
- 立即阻塞忠实复现：原始数据、环境、许可证、列定义或模型文件仍缺；硬编码路径无法映射；论文 PDF 是唯一“数据”。
- 只有作者/合法数据、环境、完整模型/CGAN/SHAP、实验候选、论文核对和偏差齐全，才可从 `blocked` 改为 `completed`。
