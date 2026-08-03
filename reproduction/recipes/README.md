# 全部论文复现路径索引

本目录为已正式收录或已完成人工核验的论文/项目提供逐篇操作路径。这里的
“路径已补齐”表示 recipe 可供执行与审计，**不表示本仓库已经得到论文结果**。
真实执行状态以 [`STATUS`](../STATUS.md) 和各次 `reproduction/runs/<ID>/`
证据为准。

统一规范见 [`PLAYBOOK_SPEC`](../PLAYBOOK_SPEC.md)，机器可读清单见
[`manifest.json`](../manifest.json)。

## 推荐执行顺序

```text
基础回归 AL
A01 → A02 → W01 → W02 → A03 → A04

结构表示与小样本不确定性
A05 → A06 → A07 → W03 → P04 → A09

相图、闭环与势函数
A08 → P05 → P07 → W04 → W05 → W06 → W07 → P09

贝叶斯优化与应用
P01 → P02 → P03 → P10 → P06 → PS01 → AD01 → H01 → L01

支持模型
S03 → S01 → S02
```

## 逐篇入口

### 模型学习型主动学习

| ID | 入口 | 执行定位 |
|---|---|---|
| A01 | [NIST structure–property AL](A01/README.md) | 普通电脑；第一篇 |
| A02 | [DAGS](A02/README.md) | 普通电脑；第一篇或第二篇 |
| A03 | [Benchmark-AL-Mat](A03/README.md) | AutoML 计算预算较高 |
| A04 | [Black-box approximation](A04/README.md) | 无作者代码；统一重实现 |
| A05 | [GP-Net](A05/README.md) | 先回放 embedding |
| A06 | [MOF RT-AL](A06/README.md) | 大数据；先单目标 |
| A07 | [UQALE](A07/README.md) | 分子 OOD 泛化 |
| A08 | [AIPHAD](A08/README.md) | 相图离线回放 |
| A09 | [ANI-1x / QBC](A09/README.md) | COMP6 小子集评估；完整历史 AL 链待锁定 |
| W01 | [Classification suite](W01/README.md) | 分类 AL |
| W02 | [Materials redundancy/QBC](W02/README.md) | RF/XGBoost/QBC |
| W03 | [MOF GNN + MC dropout](W03/README.md) | 旧 JAX/GNN 环境 |
| P04 | [PBNN / NeuroBayes](P04/README.md) | 贝叶斯神经网络 |

### 真实闭环、并发学习与势函数

| ID | 入口 | 执行定位 |
|---|---|---|
| P05 | [DKL-on-STM](P05/README.md) | 先模拟，仪器闭环另列 |
| P07 | [CAMEO](P07/README.md) | 先离线图表，真实 XRD 另列 |
| P09 | [DP-GEN](P09/README.md) | 教程/回放优先，完整流程需 HPC |
| W04 | [ALEBREW](W04/README.md) | 小体系离线回放 |
| W05 | [FLARE](W05/README.md) | 公开数据/小算例优先 |
| W06 | [SARA](W06/README.md) | 论文图回放，机器人闭环另列 |
| W07 | [FALCON](W07/README.md) | EMT smoke test，DFT 另列 |

### 贝叶斯优化、应用与平台

| ID | 入口 | 执行定位 |
|---|---|---|
| P01 | [PV-Lab benchmark](P01/README.md) | BO 基准 |
| P02 | [NIST Fe-Co-Ni](P02/README.md) | BO 与材料先验 |
| P03 | [Bgolearn](P03/README.md) | 单/多目标 BO 工具 |
| P10 | [Augmented GP](P10/README.md) | 物理先验 GP |
| P06 | [MolPAL](P06/README.md) | 大分子池 top-k |
| P08 | [CAMD](P08/README.md) | 闭环平台架构 |
| AD01 | [环氧胶黏剂](AD01/README.md) | Greedy + BO；自行重实现 |
| PS01 | [聚合物太阳能电池](PS01/README.md) | 组合材料目标搜索 |
| H01 | [锂结晶 HITL](H01/README.md) | 静态回放优先 |
| L01 | [LLM-AL](L01/README.md) | 保存轨迹回放；API 另列 |

### 支持模型

| ID | 入口 | 执行定位 |
|---|---|---|
| S01 | [固化过程 PINN](S01/README.md) | 方程/数据核验后重实现 |
| S02 | [PiNDiff-CVI](S02/README.md) | 稀疏数据＋不完整物理 |
| S03 | [DES ML](S03/README.md) | 普通监督学习支持案例 |

## 暂不建立 recipe 的观察论文

`LITERATURE_WATCH` 中 2026 观察区的分子 Pareto front、Discovery Learning、
RAFFLE、Quantum-Inspired AL、可持续玻璃、铈氢化物势函数和钢缺陷分类尚未全部
通过代码、数据、许可证与任务边界核验。
它们保留在观察区，不使用“可复现”措辞。完成准入核验并获得稳定 ID 后，才可
加入本索引和 `manifest.json`。逐篇缺口和准入步骤见
[观察论文阻塞清单](OBSERVATION_BLOCKERS.md)。
