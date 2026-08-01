# P08｜CAMD 自主材料发现闭环平台复现

**路径状态**：`offline-only`
**论文**：[Autonomous intelligent agents for accelerated materials discovery](https://doi.org/10.1039/D0SC01101K)
**正式论文卡**：[`papers/related/closed_loop_platforms/P08_CAMD.md`](../../../papers/related/closed_loop_platforms/P08_CAMD.md)

## 定位与边界

CAMD 把闭环拆成 `Agent → Experiment → Analyzer → Campaign`。它是**闭环软件平台**，不是一个固定主动学习算法。离线 `after-the-fact` Experiment 可在历史数据库上回放；论文完整端到端流程涉及 OQMD、AWS Batch、DFT/VASP 和计算资源。

- 最小复现：框架单元测试＋离线 AgentSimulation。
- 忠实软件复现：论文时期 release 上运行离线结构发现 agent/campaign。
- 完整论文实验：需要 OQMD 特征、云/HPC、VASP 许可证和 DFT 配置，普通电脑不可完成。
- 运行框架不等于复现论文发现效率；启发式 Agent 也不自动等于主动学习。

## 来源锁定

一手来源：

- 论文 DOI：`10.1039/D0SC01101K`
- 作者仓库：[TRI-AMDD/CAMD](https://github.com/TRI-AMDD/CAMD)，Apache-2.0
- 论文发表期 release：`v2020.8.28`（第一次运行还应与论文/仓库 release 日期复核）
- 官方 OQMD 特征数据入口：作者 README 指向 `https://data.matr.io/3/`

```bash
git clone --branch v2020.8.28 --depth 1 \
  https://github.com/TRI-AMDD/CAMD.git ../upstream/P08-camd
git -C ../upstream/P08-camd remote -v
git -C ../upstream/P08-camd branch --show-current
git -C ../upstream/P08-camd describe --tags --always --dirty
git -C ../upstream/P08-camd rev-parse HEAD
git -C ../upstream/P08-camd status --short
shasum -a 256 ../upstream/P08-camd/LICENSE \
  ../upstream/P08-camd/requirements.txt
```

OQMD/MatR.io 下载需记录最终 URL、许可、大小和 SHA-256；不得把 VASP、密钥、AWS 凭证或受限数据提交仓库。写入 `reproduction/runs/P08/source_lock.md`。

## 环境

环境名：`repro-p08-camd`。release 的 `requirements.txt` 已固定 2020 年依赖（含 NumPy 1.19.1、GPflow 2.1.0、scikit-learn 0.23.2 等），适合 Linux x86_64 隔离环境；其中 `git://...qmpy_py3` 可能因协议停用失败。

```bash
conda create -n repro-p08-camd python=3.7 pip -y
conda activate repro-p08-camd
cd ../upstream/P08-camd
python -m pip install numpy==1.19.1
python -m pip install -r requirements.txt
python setup.py develop
python -m pip check
python -m pip freeze > ../../Reproduction-of-Active-Learning-in-Materials-Science/reproduction/runs/P08/pip-freeze.txt
```

Python 3.7 是本路径的兼容性选择；上游 README 未固定 Python 3 小版本。若仅因 `git://` 失败，可将同一 commit URL 改为 HTTPS，并保存安装 patch；不可换浮动 qmpy `master` 而不锁 SHA。导出环境和硬件到运行目录。

## T0｜来源、角色和外部依赖核验

1. 固定 release、许可证、环境和 OQMD 数据版本。
2. 建立 `component_map.md`：Agent、Experiment、Analyzer、Campaign 的类、输入、输出和持久化文件。
3. 审计 `examples/agent_random_v2`、`agent_gp_simple`、`generic_gp_ucb`、`camd/experiment/agent_simulation.py`。
4. 区分离线 Oracle、真实 DFT 和真实实验；列出 VASP/AWS/数据库/API 的权限、费用和密钥边界。
5. 建立论文图表—campaign 配置—分析器指标映射。

## T1｜最小 smoke test

不连接 AWS/VASP，只运行离线测试：

```bash
cd ../upstream/P08-camd
pytest -q \
  camd/campaigns/tests/test_base.py \
  camd/experiment/tests/test_agent_simulation.py
```

随后运行一个 `examples/agent_random_v2` 或 `examples/generic_gp_ucb/black-box_optimization_example.ipynb` 的小预算副本。Smoke 成功要求：Campaign 能保存/恢复状态、Experiment 只返回请求候选、Analyzer 生成指标、重启不重复消费候选。

## T2｜忠实复现论文主结果

离线可做部分：

1. 取得论文使用的 OQMD 候选/种子特征并核对哈希。
2. 固定相同 seed data、预算和重复种子，运行 Random Agent 与论文的结构发现 Agent。
3. 使用 AgentSimulation/after-the-fact Oracle，保存每轮请求、返回、发现结果和 Analyzer 指标。
4. 重画发现率/加速曲线，并核对论文配置。

完整 DFT 路径仅在有明确权限后执行：

1. 在隔离云/HPC 账户配置 AWS Batch 与 VASP，不将密钥写日志。
2. 固定赝势、VASP 版本、输入参数、失败重试和成本。
3. 逐轮保存原始 DFT 输出、解析结果与失败状态。

缺 VASP/云资源时，本 recipe 保持 `offline-only`，不得声称完整论文闭环复现。

## T3｜统一平台消融

- 在同一离线候选池比较 Random、纯 Greedy、GP-UCB/不确定性 Agent。
- 保持 Experiment/Analyzer/Campaign 不变，只替换 Agent，分离算法与平台贡献。
- 注入超时、失败计算、重复结果和中断恢复，验证 campaign 状态机。
- 报告发现率、precision/recall、每个发现的查询数、累计计算成本、失败率和恢复一致性。
- 检查批量大小、异步返回和停止条件对结论的影响。

## T4｜迁移到 DGEBA/粘合剂数据

实现四个清晰模块：

- `Agent`：Random、RF/GP-UCB 或 DAGS 推荐配方；
- `Experiment`：先用 Synthetic lookup，后连接化学组实验回填；
- `Analyzer`：MAE/校准、best-so-far、可行率和失败模式；
- `Campaign`：候选状态、批次、审批、停止与恢复。

真实实验必须有人工批准和安全/可制备约束。Synthetic lookup 只验证软件闭环；不得把它当作化学发现。模型输入排除标签派生模拟量，候选 ID 与实验样本 ID 永久不可变。

## 公平性与评价

- 平台指标：状态恢复一致性、重复提交数、失败率、吞吐量和审计完整性。
- 优化指标：best-so-far、regret、发现率、达到阈值的实验数和累计成本。
- Random 是必需 Agent；策略共享候选池、seed data、预算和随机种子。
- 离线数据标签只在 Experiment 响应时揭示；Analyzer 不得向 Agent 泄露全池。
- 结构近邻、数据库时间、DFT 参数与失败样本处理必须统一。
- DFT 与 after-the-fact 结果分开，不把数据库标签称为新计算。

## 证据交付

```text
reproduction/runs/P08/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── component_map.md
├── external_requirements.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

每轮还要保留 `submitted/returned/consumed/failed` 清单和 campaign checkpoint；密钥用环境变量，绝不进入证据目录。

## 停止条件

- Smoke 成功：离线 campaign 至少完成两轮、可中断恢复且无重复候选。
- 立即阻塞：数据/许可证不明、旧依赖修复改变算法、campaign 状态不可恢复、需要 VASP/AWS 但未获权限。
- 离线论文曲线、环境、轨迹、比较与偏差齐全可标“离线复现完成”；只有真实 DFT 全链证据齐全才可把整体状态改为 `completed`。
