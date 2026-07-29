# 复现状态

状态定义：

- `已收录`：论文、分类和公开资源已核验，尚未开始运行；
- `来源锁定`：已固定论文版本、代码 commit 和数据版本；
- `环境准备`：正在建立可重复环境；
- `忠实复现`：正在运行作者原始流程；
- `结果核对`：正在与论文表格或图比较；
- `统一重实现`：正在接入统一实验接口；
- `完成`：环境、命令、日志、结果和报告均可复查；
- `阻塞`：缺少数据、软件、算力或实验条件，且已明确记录。

> `已收录` 不等于 `已复现`。当前仓库没有任何一篇达到“完成”。

## 主动学习主线

| 编号 | 论文/项目 | 类型 | 当前状态 | 下一步 |
|---|---|---|---|---|
| A01 | NIST structure–property AL | 全局回归 AL | 已收录 | 锁定 `usnistgov/active-learning` commit，检查二维弹性数据与入口 |
| A02 | DAGS | 密度感知回归 AL | 已收录 | 先用合成数据运行 Random/iGS/DAGS |
| A03 | Benchmark-AL-Mat | AutoML＋AL 基准 | 已收录 | 选择一个数据集和三种策略，估算缩小运行成本 |
| A04 | Black-box approximation | 不确定性 AL 边界研究 | 已收录 | 确认可公开取得的数据；论文专用代码未核验 |
| A05 | GP-Net | GNN embedding＋GP entropy AL | 已收录 | 下载 Zenodo embedding，先回放而不重训 MEGNet |
| A06 | MOF RT-AL | 代表性训练集 AL | 已收录 | 选择一个目标；评估 4.1 GB 数据下载需求 |
| A07 | UQALE | 分子 OOD 泛化 AL | 已收录 | 锁定代码/数据版本，只跑一个性质和一种 UQ |
| A08 | AIPHAD | 相图分类 AL | 已收录 | 安装前检查 Python 支持；设计 held-out 分类指标 |
| P04 | PBNN / NeuroBayes | 神经网络 AL | 已收录 | 完成 A01/A02 后再固定 release |
| P05 | DKL-on-STM | AL+BO 混合闭环 | 已收录 | 先运行模拟 Notebook，不连接仪器 |
| P07 | CAMEO | AL+BO 混合闭环 | 已收录 | 检查 MATLAB/MEX 环境，先理解相图风险目标 |
| P09 | DP-GEN | 势函数并发学习 | 已收录 | 只做环境、教程和小规模数据回放评估 |

## 贝叶斯优化副线

| 编号 | 论文/项目 | 当前状态 | 下一步 |
|---|---|---|---|
| P01 | PV-Lab Benchmarking | 已收录 | 主线 A01 跑通后再启动；报告 BO 指标 |
| P02 | NIST Fe-Co-Ni Benchmark | 已收录 | 核对数据下载和 starter code |
| P03 | Bgolearn | 已收录 | 运行官方单目标 CodeDemo |
| P10 | Augmented GP / GPax | 已收录 | 固定代码版本，比较普通 GP 与结构化 GP |

## 相关与支持

| 编号 | 论文/项目 | 分类 | 当前状态 | 下一步 |
|---|---|---|---|---|
| P06 | MolPAL | 分子 BO / top-k 筛选 | 已收录 | 需要分子池工程时再使用 publication tag |
| P08 | CAMD | 闭环平台 | 已收录 | 仅做架构与旧依赖评估 |
| PS01 | 聚合物太阳能电池 | NLP 数据＋目标导向 AL/BO/bandit | 已收录 | 基础 AL/BO 后固定作者 commit，先比较 Random/Greedy/GP-EI |
| H01 | 锂盐连续结晶 HITL | AL＋多目标优化＋真实闭环 | 已收录 | 固定 Zenodo v1，从带输出 notebook 做静态回放 |
| L01 | LLM-AL | LLM 驱动的离散池目标优化 | 已收录 | 先回放作者轨迹，不调用商业 API |
| S01 | 固化过程 PINN | 物理支持 | 已收录 | 确认官方代码；先读方程和 loss |
| S02 | PiNDiff-CVI | 物理支持 | 已收录 | 运行作者合成数据流程 |
| S03 | DES ML | 普通监督学习 | 已收录 | 保留为材料 ML/候选生成参考，不计入 AL |

## 当前唯一执行项

```text
A01 来源锁定
→ A01 最小闭环
→ A01 三策略学习曲线
→ A01 论文趋势核对
→ 再启动 A02
```

具体操作见 [START_HERE](START_HERE.md)。
