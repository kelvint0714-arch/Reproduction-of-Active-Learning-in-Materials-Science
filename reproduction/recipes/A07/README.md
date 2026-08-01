# A07｜UQALE 分子 OOD 主动学习复现路径

> 状态：`source-lock-needed`。作者代码依赖旧深度学习栈且含硬编码数据路径，尚未执行。

## 定位与边界

- 论文：*Evaluating uncertainty-based active learning for accelerating the generalization of molecular property prediction*，DOI：[10.1186/s13321-023-00753-5](https://doi.org/10.1186/s13321-023-00753-5)。
- 分类：改善 OOD 泛化的 AL，不是性质极值 BO；原论文重点是一次批量采集。
- 最小复现：水溶解度＋Molecular Descriptor Model，第一 PCA 方向 5 bins，比较 Random 与一个密度/UQ 加权批次。
- 忠实复现：水溶解度/氧化还原、MDM/GNN、多 UQ、前三 PCA、多个初始比例/批量、30 次重复。
- 门槛：旧 TensorFlow/PyTorch-Geometric/RDKit 环境；MDM 可 CPU/GPU，完整组合与 GNN 需 GPU。仓库脚本不是统一 CLI。

## 来源锁定

- 作者代码：[pnnl/UQALE](https://github.com/pnnl/UQALE)。
- 水溶解度：[Figshare 10.6084/m9.figshare.14552697](https://doi.org/10.6084/m9.figshare.14552697)。
- 氧化还原：[piyushtagade/SLAMDUNCS](https://github.com/piyushtagade/SLAMDUNCS)。
- 后续 OOD AL 数据：[Zenodo 10.5281/zenodo.13769710](https://doi.org/10.5281/zenodo.13769710)；后续归档不能未经核对冒充原论文输入。

```bash
git clone https://github.com/pnnl/UQALE.git ../upstream/A07-uqale
git -C ../upstream/A07-uqale remote -v
git -C ../upstream/A07-uqale branch --show-current
git -C ../upstream/A07-uqale describe --tags --always --dirty
git -C ../upstream/A07-uqale rev-parse HEAD
git -C ../upstream/A07-uqale status --short
```

分别保存原论文数据与后续 Zenodo manifest、哈希、许可证到 `reproduction/runs/A07/source_lock.md`。

## 环境

- 环境名：`repro-A07`。
- 作者 `requirements.txt` 固定 Keras 2.3.1、TensorFlow 2.1、Torch 1.5、PyG 1.5、旧 RDKit，但未声明 Python 版本；先按这些包的官方 wheel/Conda 元数据求交集，再将解析出的 Python 版本写进锁文件，不能凭年份猜版本。优先 Linux 容器/Conda，不要在当前 Python 强装。

```bash
mamba create -n repro-A07 python=<VERIFIED_COMPATIBLE_VERSION> pip -y
mamba activate repro-A07
python -m pip install -r ../upstream/A07-uqale/requirements.txt
python -m pip freeze > /ABS/PATH/reproduction/runs/A07/pip-freeze.txt
conda env export --from-history > /ABS/PATH/reproduction/runs/A07/environment.from-history.yml
```

`<VERIFIED_COMPATIBLE_VERSION>` 必须先解析后替换，不能原样执行。若旧 wheels 不可得，容器镜像 digest、手动替换项与数值差异写入 `deviations.md`，不猜测“兼容最新版”。

## T0｜来源与入口核验

1. 核对 `active_learning/sol/`、`active_learning/redox/`、`metrics/` 及所有硬编码路径。
2. 建立 `configs/file_map.yaml`，将每个 `train.csv`、相似度矩阵、PCA 坐标映射到已锁文件。
3. 对照论文确认原始脚本部分循环是 20 runs，而论文汇总可能用 30 次；必须解释/补齐，不能混报。
4. 先运行 `python -m py_compile` 检查语法；源文件中的占位赋值（如 `wdir = # ...`）必须复制后修改，原上游不改。

## T1｜最小 smoke test

1. 复制 `active_learning/sol/mdm/embed/sol_mdm_embed.py` 到 `runs/A07/src/`。
2. 只改数据路径；把 PCA 数设为 1、bins=5、runs=1、一个初始比例/批量。
3. 同一初始样本分别跑 `use_random=True/False`，保存 OOD bin、ID 和全测试集 RMSE。

成功标准：两批次大小相同、无重复、UQ 权重归一化、OOD/ID 索引互斥且两种策略输出完整。

## T2｜忠实复现论文主结果

1. 按论文使用前三 PCA，每次移除一个 bin 构造 OOD，恢复论文初始比例、批量和 30 次重复。
2. 分别复现水溶解度/氧化还原与 MDM/GNN；Random 与 UQ 使用相同拆分。
3. 报告 OOD、ID、全测试 RMSE，AL 批次中 OOD 比例及相对 Random 的百分比改善。
4. 复现 ENCE、误差相关性、OOD 检出相关性；明确改善虽可能显著但幅度小。

## T3｜统一协议与消融

- 先固定水溶解度 MDM；比较密度、MCDO/ensemble（能建立时）与 Random。
- 加真正多轮闭环作为扩展，并与论文一次批量结果分开。
- 对相似度表示（指纹/嵌入）、bin 数、批量大小、初始比例做消融。

## T4｜迁移至 DGEBA

- 用 IL/多酚结构描述符做 PCA，按结构簇或 PCA bin 人为构造 OOD。
- 比较 Random/UQ 是否更快补入缺失结构类型；主指标是 OOD Y1 RMSE，不是寻找最高 Y1。
- Synthetic 标签只做离线 oracle；未来真实实验必须记录失败/缺失标签而非删除。

## 公平性与评价

- 主指标：OOD RMSE；辅指标：ID/全测试 RMSE、改善百分比、OOD 命中率、ENCE、误差/UQ 相关性。
- 论文完全重复数、初始比例和 batch 必须按任务记录；Random/UQ 共用初始集和池。
- PCA/标准化只在训练候选分区协议允许的数据上拟合并固定；测试标签不参与采集。
- 分子去重/骨架泄漏必须检查；同分子不同表示不能跨 split。

## 证据交付

```text
reproduction/runs/A07/
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

保存每个 OOD bin 的索引、抽样概率和被选分子 ID。

## 停止条件

- smoke 成功：单任务 Random/UQ 一次批量结果及隔离断言齐全。
- 停止：硬编码路径仍为空、原/后续数据混淆、重复数与论文不符、旧环境迁移未记录、OOD 定义使用测试反馈调优。
- 只有全部任务/重复/UQ 指标和论文核对齐全才可 `completed`。
