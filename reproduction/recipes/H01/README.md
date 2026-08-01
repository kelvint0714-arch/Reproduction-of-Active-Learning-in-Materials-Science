# H01｜锂盐连续结晶 Human-in-the-Loop 主动学习复现

**路径状态**：`offline-only`
**论文**：[Human-AI synergy in adaptive active learning for continuous lithium carbonate crystallization optimization](https://doi.org/10.1039/D5DD00285K)
**正式论文卡**：[`papers/related/goal_directed_al_bo/H01_Lithium_Crystallization_HITL_2025.md`](../../../papers/related/goal_directed_al_bo/H01_Lithium_Crystallization_HITL_2025.md)

## 定位与边界

论文把回归/帕累托探索、专家收缩空间、GPC 可行域学习、真实连续结晶实验串成**人在回路 AL＋多目标过程优化**。关键可复现对象不仅是模型，还包括每轮人类为何改变边界。

- 最小复现：Zenodo 固定归档的已保存 Notebook/数据回放，重画 Pareto 和 GPC 边界。
- 忠实离线复现：运行无输出 Notebook，核对数据处理、NSGA-II、GPC、比较模拟。
- 真实闭环：需要连续结晶装置、原料、分析测试、安全审批和专家决策；普通电脑只能离线。
- 论文报告 38 次实验和电池级结果是核对目标，不可硬编码为算法输出，也不代表严格证明全局最优。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1039/D5DD00285K`
- 作者仓库：[shmouses/HITL_Adaptive_Active_Learning_Lithium](https://github.com/shmouses/HITL_Adaptive_Active_Learning_Lithium)，MIT
- 固定归档：Zenodo v1 [`10.5281/zenodo.17122531`](https://doi.org/10.5281/zenodo.17122531)
- Zenodo 文件：`HITL_Adaptive_Active_Learning_Lithium-main.zip`，页面记录 MD5 `5deabf21c672911f9ddb915b6d053fdd`；数据权利仍以归档页面为准，不能自动假设均由 GitHub MIT 覆盖。

```bash
git clone https://github.com/shmouses/HITL_Adaptive_Active_Learning_Lithium.git \
  ../upstream/H01-hitl-lithium-git
git -C ../upstream/H01-hitl-lithium-git remote -v
git -C ../upstream/H01-hitl-lithium-git branch --show-current
git -C ../upstream/H01-hitl-lithium-git describe --tags --always --dirty
git -C ../upstream/H01-hitl-lithium-git rev-parse HEAD
git -C ../upstream/H01-hitl-lithium-git status --short
curl -L \
  'https://zenodo.org/records/17122531/files/HITL_Adaptive_Active_Learning_Lithium-main.zip?download=1' \
  -o ../upstream/H01-hitl-lithium-v1.zip
openssl dgst -md5 ../upstream/H01-hitl-lithium-v1.zip
shasum -a 256 ../upstream/H01-hitl-lithium-v1.zip
```

解压到 `../upstream/H01-hitl-lithium-v1/`，记录 ZIP 和所有 CSV/XLSX/Notebook 的 SHA-256、Zenodo metadata JSON、许可与访问日期到 `reproduction/runs/H01/source_lock.md`。

## 环境

环境名采用上游 `hitl-lithium`。官方 `environment.yml` 已固定 Python 3.9、NumPy/Pandas/scikit-learn/Optuna/SHAP/Platypus 等版本。

```bash
conda env create -f ../upstream/H01-hitl-lithium-v1/environment.yml
conda activate hitl-lithium
python -m pip check
python -m pip freeze > reproduction/runs/H01/pip-freeze.txt
conda env export --no-builds > reproduction/runs/H01/environment.yml
```

上游 README 宣称脚本入口，但已核验 GitHub 某些模块化脚本内容不完整；T1/T2 优先固定归档的 `Paper_Reproduction*.ipynb`，不要因为 README 写了 `python scripts/main.py` 就假设等价。

## T0｜归档、数据与人类决策核验

1. 核对 Zenodo v1 MD5、SHA-256、环境和所有文件清单。
2. 比较 `Paper_Reproduction_with_Cell_Outputs.ipynb` 与无输出版的代码 cell 哈希，确认带输出版不是另一套代码。
3. 审计 `Data/raw`、`Data/clean`、`Data/generated` 的批次日期、列、单位、缺失和转换链。
4. 从论文/Notebook 建立 exploration（回归+Pareto/NSGA-II）和 exploitation（GPC+边界/ray tracing）流程图。
5. 为每轮人工改变范围、排除候选和批准实验建立 `human_decisions.csv`；无法从公开材料恢复的决策标 `NR`。

## T1｜最小 smoke test

先对带输出 Notebook 做静态/输出回放，不执行 API 或实验：

```bash
jupyter nbconvert --to html \
  --output-dir reproduction/runs/H01/raw_results \
  ../upstream/H01-hitl-lithium-v1/Paper_Reproduction_with_Cell_Outputs.ipynb
```

随后执行无输出 Notebook 的数据加载和一个小型分析副本：

```bash
jupyter nbconvert --execute \
  --ExecutePreprocessor.timeout=7200 \
  --to notebook \
  --output-dir reproduction/runs/H01/raw_results \
  --output paper_reproduction_smoke.ipynb \
  ../upstream/H01-hitl-lithium-v1/Paper_Reproduction.ipynb
```

若全本过重，只执行到第一幅数据/Pareto 图并保存 cell 选择清单。Smoke 成功要求：所有数据路径解析、数据处理行数与带输出版一致、GPR/GPC 至少各拟合一次且输出有限。

## T2｜忠实复现论文主结果

1. 在 Zenodo 环境完整执行无输出 Notebook，不以 GitHub 空脚本替代。
2. 核对每批原始→清洗数据和论文阶段边界。
3. 重跑 GPR/模型选择、LHS 候选生成、Pareto/NSGA-II、GPC 决策边界和比较模拟。
4. 保存每轮训练数据、候选空间、模型、推荐点、专家修改和实验结果。
5. 对照 38 次实验、产品质量/杂质阈值、镁容忍范围、论文 Pareto/边界/比较图。
6. 真实设备操作不在离线复现范围；历史实验结果作为 Oracle 回放，明确标注。

## T3｜统一协议与 HITL 消融

- 比较 Random、无专家自动规则、只用固定可行域、论文 HITL 四组。
- 保持相同起始批次、候选生成预算和历史 Oracle；把人工修改写成可回放规则或逐轮日志。
- 对移除冷端温度等关键特征、改变可行阈值和候选密度做消融。
- 分类报告 AUROC/AUPRC、Brier、校准和可行域 recall；多目标报告 hypervolume/可行率；优化报告达到电池级的实验数。
- 用 bootstrap/配对模拟报告不确定性，不能只比较一条真实历史路径。

## T4｜迁移到 DGEBA/粘合剂数据

采用“模型推荐—化学组审核—实验—回填”的 HITL 结构。化学组审核可制备性、安全、相容性和测试资源；所有拒绝/改动必须有理由码，避免不可审计的人为选择。

探索阶段先覆盖结构/配方空间和可行域，优化阶段再找高强度。Synthetic 表只作为离线 Oracle；真实实验模板需记录批次、单位、固化、基材、测试标准、重复和失败模式。固定结构对的数据足够后才做小数比例 BO。

## 公平性与评价

- 可行域分类：AUROC/AUPRC、Brier、ECE、决策阈值下 precision/recall，类别不平衡时不只报 accuracy。
- 多目标：Pareto recall、hypervolume、可行率和约束违反。
- 过程：达到合格条件的实验数、成功率、累计成本和专家修改次数。
- Random 与无专家规则是必要对照；共享初始数据、候选池、预算和随机种子。
- 时间回放严格禁止未来批次参与早期特征缩放/超参选择。
- 人类决策若无法记录，不能归因“Human-AI synergy”的增益。

## 证据交付

```text
reproduction/runs/H01/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── data_manifest.csv
├── human_decisions.csv
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

## 停止条件

- Smoke 成功：固定归档可读，数据转换行数匹配，至少一个 GPR/GPC 分析可执行。
- 立即阻塞：Zenodo 哈希不符、权利不明、Notebook 代码/输出版不一致、关键人工边界无法恢复却被当算法规则。
- 离线证据齐全可标“offline reproduction completed”；只有装置、逐轮专家日志、真实实验与全部论文核对齐全，整体状态才可 `completed`。
