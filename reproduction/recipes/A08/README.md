# A08｜AIPHAD 主动相图构建复现路径

> 状态：`source-lock-needed`。Python 工具可回放；真实 Fe–Ti–Sn 实验属于 `offline-only` 边界，未声称已执行。

## 定位与边界

- 论文：*AIPHAD, an active learning web application for visual understanding of phase diagrams*，DOI：[10.1038/s43246-024-00580-7](https://doi.org/10.1038/s43246-024-00580-7)。
- 分类：相图分类/边界学习 AL，不是连续性质 BO。
- 核心：RBF 图上的 Label Propagation/Spreading；LC、MS、EA、Random；批量可用 Neighbor Exclusion。
- 最小复现：公开低维相图数据隐藏标签，离线比较 LC/MS/EA/RS。
- 忠实边界：Supplementary Data 可回放；真实新样制备与 XRD 需要化学实验室和专家判相。

## 来源锁定

- 官方代码：[NIMS-DA/aiphad](https://github.com/NIMS-DA/aiphad)。
- 官方文档：[AIPHAD documentation](https://nims-da.github.io/aiphad/docs/en/index.html)。
- NIMS 数据记录：[MDR dataset](https://mdr.nims.go.jp/datasets/1473a8e6-5355-4091-bb8a-ab059bb6ed17)。
- 论文数据还包括 Supplementary Data 1–5；逐文件记录哈希。

```bash
git clone https://github.com/NIMS-DA/aiphad.git ../upstream/A08-aiphad
git -C ../upstream/A08-aiphad remote -v
git -C ../upstream/A08-aiphad branch --show-current
git -C ../upstream/A08-aiphad describe --tags --always --dirty
git -C ../upstream/A08-aiphad rev-parse HEAD
git -C ../upstream/A08-aiphad status --short
shasum -a 256 /ABS/PATH/TO/SUPPLEMENTARY_DATA_*
```

记录代码 MIT 许可证、数据许可/引用和哈希于 `reproduction/runs/A08/source_lock.md`；网页仅作 UI，对复现以固定 Python SHA 为准。

## 环境

- 环境名：`repro-A08`。
- 作者 `setup.py` 声明 Python≥3.6，依赖 matplotlib/numpy/physbo/scikit-learn/scipy；从锁定源码安装。

```bash
mamba create -n repro-A08 python pip -y
mamba activate repro-A08
python -m pip install ../upstream/A08-aiphad
python -c "import aiphad; print(aiphad.__file__)"
conda env export --from-history > /ABS/PATH/reproduction/runs/A08/environment.from-history.yml
python -m pip freeze > /ABS/PATH/reproduction/runs/A08/pip-freeze.txt
```

记录 PHYSBO/scikit-learn 版本；LabelPropagation 的版本变化可能改变概率。

## T0｜来源与入口核验

1. 核对 `pdc_sampler` 参数：`page_type`、`estimation`（LP/LS）、`sampling`（LC/MS/EA/RS）、proposal、NE。
2. 将 Supplementary Data 的坐标、相标签、已测/未测标记映射成 X 与 y（未标记为 `-1`）。
3. 固定完整真值副本、初始可见标签和 held-out 评价索引；真值文件只由离线 oracle 读取。

## T1｜最小 smoke test

在 `runs/A08/src/smoke.py` 构造二维网格与三类标签，保留每类至少两个初始点：

```python
from aiphad import pdc_sampler
pdc = pdc_sampler(
    page_type="two_variables", estimation="LP", sampling="EA",
    proposal=1, parameter_constraint=False, multi_method="OU"
)
pdc.fit(X, y_masked)
pdc.us()
assert len(pdc.uncertainty_index) == 1
```

成功标准：拟合完成、建议索引来自 `y=-1` 的池、揭示后能进入下一轮。

## T2｜忠实复现论文主结果

1. 使用 Supplementary Data 复建论文 Fe–Ti–Sn 初始已测点与每轮新增点。
2. 按论文配置回放 LP/LS、相应不确定性和 Neighbor Exclusion，保存每轮概率图、相图和建议。
3. 比较复现建议与论文实际实验序列；真实实验标签只能作为离线 oracle。
4. 论文主要是案例可视化，不能捏造统一测试指标；数值评价只作为本项目补充。

## T3｜统一协议与消融

- 从完整相图重复随机隐藏标签，比较 LC/MS/EA/RS；每种 20 个相同初始种子。
- 指标：macro-F1、balanced accuracy、边界带准确率、达到阈值所需标签、批次多样性。
- 消融 LP/LS、RBF gamma/alpha、单点/批量、OU/NE；保存查询索引。

## T4｜迁移至 DGEBA

- 仅当标签是离散相容/失效模式/可行性类别时迁移；连续强度预测不应硬套 AIPHAD。
- 候选坐标可为两个 loading 或降维配方空间；已实验类别为标签，`-1` 为待实验。
- 用于学习可行域/相边界后，再把可行候选交给独立 BO 优化强度。

## 公平性与评价

- Random 必须存在；同一初始标签、预算、batch、LP/LS 参数和种子。
- 分类指标：macro-F1、balanced accuracy、边界误差；效率：达到阈值的查询数。
- 每类初始至少有标签；held-out 真值不得参与采集或超参选择。
- 相图相邻点高度相关，应报告空间块留出；真实 XRD 判相不确定性需保留。

## 证据交付

```text
reproduction/runs/A08/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

逐轮保存 y 掩码、建议索引、概率、相图和 oracle 来源。

## 停止条件

- smoke 成功：建议合法且一次回填后可重训。
- 停止：某类无初始标签、Supplementary Data 未锁、真值进入模型输入、网页结果无法映射到固定代码 SHA。
- 离线回放和统一评价齐全可完成软件复现；没有真实合成/XRD 证据时必须继续标注 `offline-only`，不能称完整实验闭环 `completed`。
