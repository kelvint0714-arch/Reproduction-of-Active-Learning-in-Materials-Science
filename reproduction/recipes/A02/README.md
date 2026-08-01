# A02｜DAGS 密度感知主动学习复现路径

> 状态：`source-lock-needed`。本文没有声称已运行 DAGS。

## 定位与边界

- 论文：*Density-aware active learning for materials discovery: a case study on functionalized nanoporous materials*，DOI：[10.1039/D5CP02908B](https://doi.org/10.1039/D5CP02908B)。
- 分类：回归 AL；目标是降低整个空间的预测误差，不是 EI/UCB 式 BO。
- 核心：XGBoost 代理；DAGS 将 iGS 输入/输出距离分数乘以 KNN 局部密度权重。
- 最小复现：一个均匀和一个非均匀合成函数，比较 Random/iGS/DAGS；忠实复现扩为全部合成任务和 O₂/N₂/CH₄/H₂/He 等真实任务。
- 门槛：合成任务 CPU 可跑；作者 `requirements.txt` 是 Linux/GPU 型 Conda 显式清单，macOS 不能原样使用。

## 来源锁定

- 作者代码：[insane-group/Density_Aware_Greedy_Sampling](https://github.com/insane-group/Density_Aware_Greedy_Sampling)。
- O₂/N₂ 数据：[ibarisorhan/MOF-O2N2](https://github.com/ibarisorhan/MOF-O2N2)。
- CH₄/H₂/He 数据：[hdaglar/MOF-basedMMMs_ML](https://github.com/hdaglar/MOF-basedMMMs_ML)。
- 补充信息：[RSC supplementary information](https://www.rsc.org/suppdata/d5/cp/d5cp02908b/d5cp02908b1.pdf)。

论文数据可用性声明称代码版本为 v1.0.0，但官方 GitHub 当前没有可解析的同名 tag/release；因此必须锁 SHA，不能伪造 tag：

```bash
git clone https://github.com/insane-group/Density_Aware_Greedy_Sampling.git ../upstream/A02-dags
git -C ../upstream/A02-dags remote -v
git -C ../upstream/A02-dags branch --show-current
git -C ../upstream/A02-dags describe --tags --always --dirty
git -C ../upstream/A02-dags rev-parse HEAD
git -C ../upstream/A02-dags status --short
shasum -a 256 ../upstream/A02-dags/requirements.txt ../upstream/A02-dags/main.py
```

真实数据另行锁其仓库 SHA/ZIP 哈希及原始文件名；写入 `reproduction/runs/A02/source_lock.md`。

## 环境

- 环境名：`repro-A02`。
- Linux 且满足作者清单时优先：`./env_setup.sh repro-A02 mamba`。
- 非 Linux 或无 CUDA 时建立 CPU 兼容环境属于偏差：先从源码 imports 生成最小清单并在 `deviations.md` 说明，不能把作者的 `_py-xgboost-mutex=gpu_0` 悄悄删掉后仍称“原环境”。

```bash
cd ../upstream/A02-dags
./env_setup.sh repro-A02 mamba
mamba activate repro-A02
python main.py --help
conda env export --from-history > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A02/environment.from-history.yml
conda list --explicit > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/A02/environment.explicit.txt
```

记录 CPU/GPU、XGBoost 版本及是否启用 GPU；不要凭猜测固定 Python 版本。

## T0｜来源与入口核验

1. 核对 `main.py`、`active_learning.py`、`al_methods.py`、`synthetic_datasets.py` 和 `env_setup.sh`。
2. `python main.py --help` 必须显示 `dags, igs, qbc, rt, random, all`。
3. 核对源码事实：默认 XGBRegressor 参数、`designspace_thres=150`、10 次运行及 seed `(i+1)*10`，写入配置快照。

## T1｜最小 smoke test

```bash
cd ../upstream/A02-dags
python main.py -d forrester_imb -m random -i 1 -s /ABS/PATH/reproduction/runs/A02/raw_results
python main.py -d forrester_imb -m igs    -i 1 -s /ABS/PATH/reproduction/runs/A02/raw_results
python main.py -d forrester_imb -m dags   -i 1 -s /ABS/PATH/reproduction/runs/A02/raw_results
```

成功标准：三种策略各生成一份可读 CSV，包含从初始集到 150 标签的轨迹/误差字段；三份运行使用可核对的同一数据生成设置。单次胜负不作为结论。

## T2｜忠实复现论文主结果

1. 对论文均匀/非均匀合成任务运行 Random、iGS、QBC、RT、DAGS；每个任务 10 次。
2. 下载并锁定真实数据；先从 O₂ 开始，再覆盖论文五个扩散设计空间。
3. 保持 150 的标签预算、作者 XGBoost 参数、初始化/种子规则；输出测试 MAE—查询数的均值和误差带。
4. 核对“多数非均匀空间 DAGS 优于 iGS，但 He 可能由 iGS 更好”的边界，而不是只报有利任务。

## T3｜统一协议与消融

- 在相同 10 个初始索引上比较五种策略；加 `DAGS-without-density`（即 iGS）和密度 K/归一化消融。
- 统一保存每轮查询索引、局部密度、iGS 分数、乘积分数和测试预测。
- 增加 5/10/20 初始点、batch=1 与批量选择敏感性；仅用训练池拟合标准化器。

## T4｜迁移至 DGEBA

1. 读取 `ML_Training_Dataset`，以离子液体/多酚原始描述符和两个 loading 为输入，先预测 Y1。
2. 结构对分组划分测试集；避免同一 IL/多酚组合跨池与测试集造成结构泄漏。
3. 离线 oracle 每轮揭示 Synthetic Y1；比较 Random/iGS/DAGS/RT。
4. 报告 MAE—标签数与所选结构/配比覆盖度；Synthetic 结果只用于方法筛选，不能作为实验发现。

## 公平性与评价

- 主指标：测试 MAE；辅指标：RMSE、达到同一 MAE 所需查询数、学习曲线 AUC、策略耗时。
- 初始集、预算 150、batch、XGBoost 超参数与种子必须跨策略完全一致；至少论文 10 次重复。
- Random、iGS、QBC、RT 是必要基线；所有超参数只用训练/验证信息。
- 真实 MOF 数据按结构/来源去重；目标列绝不进入特征；候选池标签仅由离线 oracle 在被查询后释放。

## 证据交付

```text
reproduction/runs/A02/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── environment.explicit.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

必须保存查询索引和聚合前 CSV，不能只提交最终图片。

## 停止条件

- smoke 成功：三策略在同一合成任务上完整产生 150 标签轨迹。
- 停止并标记阻塞：官方版本号无法映射且 SHA 未记录、真实数据列映射不明、CPU 环境改变算法、策略间初始集不一致或结果仅剩聚合图。
- 只有来源/数据哈希、环境、10 次全部策略结果、论文图表核对和偏差说明齐全才能标记 `completed`。
