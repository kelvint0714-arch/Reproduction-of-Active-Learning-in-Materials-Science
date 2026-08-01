# A06｜MOF Regression Tree Active Learning 复现路径

> 状态：`source-lock-needed`。作者代码与 4.05 GB 数据已定位，但尚未执行。

## 定位与边界

- 论文：*Informative Training Data for Efficient Property Prediction in Metal–Organic Frameworks by Active Learning*，DOI：[10.1021/jacs.3c13687](https://doi.org/10.1021/jacs.3c13687)。
- 分类：回归 AL，不是 BO。Regression Tree 负责分区/选点，Random Forest 评价性质映射。
- 最小复现：仓库 `Example/` 的 QMOF PBE band gap＋Stoichiometric-120 描述符，比较 RT-AL 与 Random。
- 忠实复现：Zenodo 中 QMOF/hMOF/dMOF 多目标、多描述符与论文训练预算。
- 门槛：示例 CPU；完整数据 4.05 GB，需足够磁盘/内存，批量 RF 运行可多核。

## 来源锁定

- 作者代码：[AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs](https://github.com/AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs)。
- 数据/补充包：[Zenodo 10.5281/zenodo.10511345](https://doi.org/10.5281/zenodo.10511345)，文件 `RT-AL_MOFs_data.zip`，记录页给出 MD5 `cc6f307ba425fc55814e3f1b3d820855`。

```bash
git clone https://github.com/AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs.git ../upstream/A06-rt-al-mofs
git -C ../upstream/A06-rt-al-mofs remote -v
git -C ../upstream/A06-rt-al-mofs branch --show-current
git -C ../upstream/A06-rt-al-mofs describe --tags --always --dirty
git -C ../upstream/A06-rt-al-mofs rev-parse HEAD
git -C ../upstream/A06-rt-al-mofs status --short
shasum -a 256 ../upstream/A06-rt-al-mofs/Example/stoich120_fingerprints.csv \
  ../upstream/A06-rt-al-mofs/Example/labels.csv
```

大包下载后同时验证 Zenodo MD5 和 SHA-256；数据许可/再分发条件写入 `reproduction/runs/A06/source_lock.md`。

## 环境

- 环境名：`repro-A06`。
- 仓库未提供锁定环境；从示例实际 imports 建立最小环境，不猜测论文未声明的版本。

```bash
mamba create -n repro-A06 python numpy pandas scipy scikit-learn matplotlib jupyter nbconvert -y
mamba activate repro-A06
python -c "import numpy,pandas,scipy,sklearn; print(sklearn.__version__)"
conda env export --from-history > /ABS/PATH/reproduction/runs/A06/environment.from-history.yml
conda list --explicit > /ABS/PATH/reproduction/runs/A06/environment.explicit.txt
```

记录 CPU/线程；若版本变化导致树叶分区或 RF 结果变化，作为偏差。

## T0｜来源与入口核验

1. 核对 `RT-AL.py`、`regression_tree.py`、`Example/RT-AL_MOFs_example.ipynb`。
2. 验证示例 refcode 顺序、描述符/标签行数与唯一性。
3. 从源码固定论文示例设置：10 runs、初始 20、训练规模 40…1000、RT leaf 最小 5、RF 50 树/leaf 最小 3。

## T1｜最小 smoke test

在上游根目录运行一个不依赖论文性能结论的类级 smoke：

```bash
cd ../upstream/A06-rt-al-mofs
python - <<'PY'
import numpy as np
from regression_tree import Regression_Tree
X = np.arange(120, dtype=float).reshape(40, 3)
y = np.sin(X[:, 0] / 10)
idx = [0, 10, 20, 30]
rt = Regression_Tree(seed=0, min_samples_leaf=2)
rt.input_data(X, idx, y[idx])
rt.fit_tree()
rt.al_calculate_leaf_proportions()
chosen = rt.pick_new_points(num_samples=2)
assert len(chosen) == 2 and not set(chosen) & set(idx)
print(chosen)
PY
```

成功标准：选出两个未标记且不重复的索引；这不证明材料结果。

## T2｜忠实复现论文主结果

1. 执行 `Example/RT-AL_MOFs_example.ipynb` 并将输出 notebook 写入 runs 目录；核对作者附带的 `Results/*.csv`。
2. 为同一 10 个 train/test split 实现 Random 基线；所有训练规模与 RF 参数一致。
3. 下载 Zenodo 完整包后，按论文逐一跑 QMOF/hMOF/dMOF、带隙/吸附目标和描述符。
4. 保存每轮所选 MOF refcode、测试预测、MAE 和运行时间；不能只比较最终 1000 点。

## T3｜统一协议与消融

- 固定测试集后比较 RT-AL、Random、iGS；共享初始 20 和训练预算。
- 消融 leaf size、批量大小、代表性/多样性变体；报告重复方差。
- 增加结构族/拓扑分组留出，检查随机拆分是否高估泛化。

## T4｜迁移至 DGEBA

- 用 DGEBA 表格描述符替代 MOF Stoich-120，目标先取 Y1。
- 每个种子固定结构对分组测试集、初始 20、20 点增量；比较 RT-AL/Random。
- 记录树叶中的响应方差与所选配方；排除由 Synthetic 目标派生的中间量。

## 公平性与评价

- 主指标：固定测试 MAE；辅指标：RMSE、\(R^2\)、达到目标 MAE 所需标签、学习曲线 AUC。
- 论文示例 10 runs；Random/RT 使用相同 split、初始样本、训练规模和最终 RF。
- 标准化/特征筛选仅由训练池拟合；refcode/结构近重复不能跨测试。
- RT 的叶内响应方差只能由当前已标记样本计算；验证未标记池在查询前保持 `None`，不得提前读取其标签。

## 证据交付

```text
reproduction/runs/A06/
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

必须交付 refcode 查询轨迹和固定测试索引。

## 停止条件

- smoke 成功：Regression_Tree 完成一次有效选点。
- 停止：Zenodo 哈希/许可不清、描述符与标签错位、Random 未复用 split、真实部署成本边界未说明。
- 固定来源、10 runs、多数据结果、论文图表核对和偏差齐全后才可 `completed`。
