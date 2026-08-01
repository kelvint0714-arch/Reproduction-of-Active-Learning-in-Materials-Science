# W02｜大型材料数据冗余与不确定性主动学习复现路径

> 状态：`source-lock-needed`。优先复现作者提供的 JARVIS22 QBC demo；未声称已运行。

## 定位与边界

- 论文：*Exploiting redundancy in large materials datasets for efficient machine learning with less data*，DOI：[10.1038/s41467-023-42992-y](https://doi.org/10.1038/s41467-023-42992-y)。
- 分类：数据冗余分析＋回归 AL；目标是构造小而信息充分的训练集，不是找性质极值。
- 最小复现：JARVIS22 Matminer 描述符、形成能、QBC 与 Random。
- 忠实复现：MP/JARVIS/OQMD 多快照、形成能/带隙、pruning、RF-U/XGB-U/QBC/Random，另含 ID/OOD 与模型迁移。
- 门槛：demo 数据约 222 MB、CPU 可跑；全数据最大单文件 2.5 GB，ALIGNN/GPU 与完整循环成本高。

## 来源锁定

- 作者代码：[mathsphy/paper-data-redundancy](https://github.com/mathsphy/paper-data-redundancy)。
- 固定数据：[Zenodo 10.5281/zenodo.8200972](https://doi.org/10.5281/zenodo.8200972)。
- 代码有 `v1.0` tag，优先固定：

```bash
git clone https://github.com/mathsphy/paper-data-redundancy.git ../upstream/W02-data-redundancy
git -C ../upstream/W02-data-redundancy fetch --tags --force
git -C ../upstream/W02-data-redundancy checkout --detach v1.0
git -C ../upstream/W02-data-redundancy remote -v
git -C ../upstream/W02-data-redundancy describe --tags --always --dirty
git -C ../upstream/W02-data-redundancy rev-parse HEAD
git -C ../upstream/W02-data-redundancy status --short
```

Zenodo 给 `jarvis22_featurized_matminer.pkl` 的 MD5 为
`0d16060701e26ea18ef22bdd8bee69bb`；同时生成 SHA-256。完整复现逐个锁 MP18/21、JARVIS18/22、OQMD14/21，不得使用滚动数据库替代快照。

## 环境

- 环境名：`repro-W02`。
- 作者 `setup_env.bash`（Python 3.10）硬编码环境名 `test`；下列命令等价转录其基础依赖并改用独立名称。其中 `py-xgboost-gpu`/DGL CUDA wheels 是 Linux GPU 路线。

```bash
mamba create -n repro-W02 python=3.10 -y
mamba install -n repro-W02 -c conda-forge \
  scikit-learn py-xgboost-gpu pandas matplotlib pymatgen -y
mamba run -n repro-W02 python -m pip install ibug
conda activate repro-W02
python -c "import sklearn,xgboost,pymatgen; print(sklearn.__version__, xgboost.__version__)"
conda env export --from-history > /ABS/PATH/reproduction/runs/W02/environment.from-history.yml
python -m pip freeze > /ABS/PATH/reproduction/runs/W02/pip-freeze.txt
```

若 CPU 化，另建 `repro-W02-cpu` 并记录替换；不得把 CPU 偏差写回作者环境。

## T0｜来源与入口核验

1. 核对 `codes/get_featurized_data.bash`、`run_al.bash`、`run_al.py`、`uncertaintyAL.py`。
2. 下载 JARVIS22 文件后验证 MD5/SHA-256，检查 DataFrame 的 ID、特征、e_form/bandgap 与重复。
3. 固定 `get_data()` 的 ID/OOD split、初始比例、`stepFrac`、`trainFracStop` 和 random seed。
4. 核对允许策略字符串：`random`、`QBC`、`rfMaxUncertainty`、`xgbMaxUncertainty_ibug`。

## T1｜最小 smoke test

```bash
cd ../upstream/W02-data-redundancy/codes
bash get_featurized_data.bash
python run_al.py --growingCriteria random --dataset jarvis22 --target e_form \
  --outputDir /ABS/PATH/reproduction/runs/W02/raw_results/random \
  --stepFrac 0.05 --trainFracStop 0.10 --randomSeed 1
python run_al.py --growingCriteria QBC --dataset jarvis22 --target e_form \
  --outputDir /ABS/PATH/reproduction/runs/W02/raw_results/QBC \
  --stepFrac 0.05 --trainFracStop 0.10 --randomSeed 1
```

成功标准：RF/XGB 结果 CSV 与选中索引均生成；两策略使用相同测试集、初始比例和预算。

## T2｜忠实复现论文主结果

1. 先按 `run_al.bash` 对 JARVIS22 的 e_form/bandgap 跑 QBC；增加 Random、RF-U、XGB-U 和论文重复数。
2. 恢复论文训练比例网格，复现 ID RMSE 学习曲线和 pruning 对照。
3. 下载其余固定快照，复现 ID/OOD、formation energy/bandgap、RF/XGB/ALIGNN。
4. 保存训练索引以检验“最多 95% 可删”的条件及不同模型/性质间迁移，不只保存均值。

## T3｜统一协议与消融

- 固定一个数据×目标，比较 Random/QBC/RF-U/XGB-U/pruning；10 个相同初始 seeds。
- 消融不确定性估计、step size、模型；同一选择子集分别训练 RF/XGB。
- 按组成/化学系统分组构造 OOD，防止随机近重复掩盖泛化问题。

## T4｜迁移至 DGEBA

- 将 IL/多酚/配方组合视为候选池，比较 Random/QBC/RF-U 对 Y1 的标签效率。
- 报告压缩到 5/10/20/…% 数据时 ID 与结构 OOD 误差；避免只看随机测试集。
- 排除 Synthetic 标签派生特征；真实数据到来后保持原 Synthetic/real 来源字段。

## 公平性与评价

- 主指标：ID/OOD RMSE；辅指标：MAE、\(R^2\)、同误差所需标签比例、训练时间。
- Random、QBC、RF-U、XGB-U 使用相同 split/初始集/step/budget/seed；论文随机基线按规定重复。
- 测试和 OOD 标签不得进入选样；Matminer 特征处理只在训练协议允许范围拟合。
- 数据快照和 material ID 去重是硬条件；不同数据库间同结构重叠需报告。

## 证据交付

```text
reproduction/runs/W02/
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

必须交付 Zenodo manifest、训练索引、ID/OOD 索引与每轮 CSV。

## 停止条件

- smoke 成功：Random/QBC 10% 预算输出和索引完整。
- 停止：用当前在线数据库替代快照、数据哈希错误、GPU→CPU 改动未记录、不同策略 split/初始集不一致、OOM 后擅自下采样。
- 全快照、多模型/目标、重复结果与论文图表核对齐全后才能 `completed`。
