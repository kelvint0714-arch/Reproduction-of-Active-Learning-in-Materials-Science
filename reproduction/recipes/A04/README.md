# A04｜材料黑箱函数不确定性主动学习复现路径

> 状态：`reimplementation-only`。作者专用实验代码与整理数据未公开核实；以下是可审计的重实现路线，不代表已经运行。

## 定位与边界

- 论文：*Performance of uncertainty-based active learning for efficient approximation of black-box functions in materials science*，DOI：[10.1038/s41598-024-76800-4](https://doi.org/10.1038/s41598-024-76800-4)。
- 分类：US 与 TS-\(\mu\) 是全局函数逼近 AL；保留均值的 TS 是论文中的 BO 对照。
- 目标：检验不确定性选样何时优于 Random，以及高维/不平衡描述符何时令其失效。
- 最小复现：自建完全公开的低维材料表与高维描述符表，重实现 Random/US/TS-\(\mu\)/TS。
- 忠实边界：论文专用脚本未公开，部分整理数据需向作者申请，PoLyInfo 受访问条件约束；缺少这些文件时只能复现方法和趋势，不能声称复现全部论文数值。
- 门槛：表格任务 CPU；200 次重复可并行。无作者代码，任何实现差异都必须登记。

## 来源锁定

- 正式论文及 Methods/Data availability：[Scientific Reports](https://www.nature.com/articles/s41598-024-76800-4)。
- 开放全文：[PMC11541781](https://pmc.ncbi.nlm.nih.gov/articles/PMC11541781/)。
- 论文使用的公开软件：[PHYSBO](https://github.com/issp-center-dev/PHYSBO)、[scikit-learn](https://scikit-learn.org/)。

PHYSBO 只是依赖，不是论文专用代码。先锁依赖，再在
`reproduction/runs/A04/source_lock.md` 写明“无作者实验仓库”：

```bash
git clone https://github.com/issp-center-dev/PHYSBO.git ../upstream/A04-physbo
git -C ../upstream/A04-physbo remote -v
git -C ../upstream/A04-physbo branch --show-current
git -C ../upstream/A04-physbo describe --tags --always --dirty
git -C ../upstream/A04-physbo rev-parse HEAD
git -C ../upstream/A04-physbo status --short
shasum -a 256 /ABS/PATH/TO/EACH_INPUT_DATASET
```

每个公开替代数据记录 DOI/快照日期/许可证/哈希；若获得作者数据，保留原始文件只读副本并重新锁哈希。

## 环境

- 环境名：`repro-A04`。
- 先从论文 Methods 确认所用 PHYSBO 世代；当前 PHYSBO `main` 不能冒充 2024 论文环境。

```bash
mamba create -n repro-A04 python pip numpy scipy pandas scikit-learn matplotlib -y
mamba activate repro-A04
python -m pip install ../upstream/A04-physbo
python -c "import physbo, sklearn; print(physbo.__file__, sklearn.__version__)"
conda env export --from-history > /ABS/PATH/reproduction/runs/A04/environment.from-history.yml
python -m pip freeze > /ABS/PATH/reproduction/runs/A04/pip-freeze.txt
```

记录 CPU、线程数和线性代数后端；PHYSBO 版本变化单列为偏差。

## T0｜来源与入口核验

1. 从论文逐项录入每个任务的样本数、描述符、标签、初始数、迭代数和重复数。
2. 验证论文划分：输出范围切成 100 个 bin，每个非空 bin 抽一个验证点；余下为训练池。
3. 固化四种分数：Random、\(\sigma(x)\)、TS-\(\mu\)、TS；确认只有 TS 保留预测均值。
4. 建立 `configs/task_manifest.csv`，每行标记 `exact`、`public-substitute` 或 `unavailable`。

## T1｜最小 smoke test

在 `reproduction/runs/A04/` 重实现单文件驱动：

1. 选一个公开、低维、无缺失的材料回归表；
2. 初始点 10，单点查询 20 轮，种子 0；
3. 用同一 GPR 比较 Random 与 US；
4. 输出逐轮验证 \(R^2\)、查询索引和预测标准差。

成功标准：两策略均完成、索引无重复、候选标签只在查询后加入训练，且验证集从未进入采集。

## T2｜忠实复现论文主结果

1. 获得并锁定论文所用数据后，严格复现 100-bin 验证划分、10 个初始点和 200 次独立重复。
2. 对每个任务运行 Random/US/TS-\(\mu\)/TS；分别用 GPR 和 RFR 评价预测精度。
3. 复现验证 \(R^2\) 曲线及前 100 步
   \(\langle\Delta R^2\rangle\)；按任务报告均值/标准差。
4. 未获得的任务在主表中留空并标 `not available`，不得用替代数据填入论文对照栏。

## T3｜统一协议与消融

- 用同一公开数据构造低维原始表示和高维 Matminer/指纹表示，保持样本与标签不变。
- 对描述符标准化、PCA 维数、初始集大小做消融；全部变换只在当前训练池拟合。
- 另做固定 held-out split，检查论文的输出分层验证是否改变结论。

## T4｜迁移至 DGEBA

- 先用实验前描述符＋loading 预测 Y1；比较低维手工性质与高维 ECFP/结构描述符。
- 按 IL/多酚结构对分组留出，运行 Random/US/TS-\(\mu\)；TS 仅作为“寻找高值”的 BO 对照，不能混入 AL 排名。
- 重点检验高维、小样本下 US 是否不优于 Random；负结果同样是有效结果。

## 公平性与评价

- 主指标：验证/测试 \(R^2\)；辅指标：MAE、RMSE、前 100 步平均 \(\Delta R^2\)、学习曲线 AUC。
- 论文协议：初始 10、单点查询、200 次重复；所有策略共享每次初始索引和验证集。
- 必须有 Random；TS 与 US 分开标注 AL/BO。测试标签不能用于超参数、停止或采集。
- 输出分层本身使用标签，只能用于离线评估集构造，不能在真实在线场景伪称无需全标签。

## 证据交付

```text
reproduction/runs/A04/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── configs/
├── src/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

`comparison.md` 必须把 exact、替代任务和无法取得的数据分栏。

## 停止条件

- smoke 成功：数据隔离断言通过且 Random/US 产生完整曲线。
- 停止：作者数据/参数未知却试图对齐论文数值、验证集进入训练或采集、TS 被错误标成纯 AL。
- 只有代码、数据哈希、200 次结果、论文图表核对和全部偏差齐全才可 `completed`；否则保持 `reimplementation-only`。
