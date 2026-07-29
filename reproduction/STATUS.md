# 复现状态

状态定义：

- `未开始`：只完成文献收集；
- `环境准备`：正在固定数据、依赖和代码版本；
- `忠实复现`：运行作者原始流程；
- `结果核对`：与论文表格或图进行比较；
- `统一重实现`：接入统一实验接口；
- `完成`：结果、环境、日志和报告均可复查；
- `阻塞`：明确记录缺少的数据、软件或实验条件。

| 编号 | 论文/项目 | 当前状态 | 下一步 |
|---|---|---|---|
| P01 | PV-Lab Benchmarking | 未开始 | 锁定仓库 commit，选择仓库自带的小型数据集 |
| P02 | NIST Fe-Co-Ni Benchmark | 未开始 | 核对数据下载和 starter code |
| P03 | Bgolearn | 未开始 | 运行官方单目标回归 CodeDemo |
| P04 | PBNN / NeuroBayes | 未开始 | 固定 release 并运行主动学习示例 |
| P05 | DKL-on-STM | 未开始 | 运行模拟 Notebook |
| P06 | MolPAL | 未开始 | 使用 publication tag 和小型数据 |
| P07 | CAMEO | 未开始 | 检查 MATLAB/MEX 环境 |
| P08 | CAMD | 未开始 | 隔离旧依赖环境 |
| P09 | DP-GEN | 未开始 | 只做环境与教程可行性评估 |
| P10 | Augmented GP / GPax | 未开始 | 固定论文代码版本，运行普通 GP 与结构化 GP |
| S01 | 固化过程 PINN | 未开始 | 确认有无官方代码；先读方程与 loss |
| S02 | PiNDiff-CVI | 未开始 | 运行作者合成数据流程 |
| S03 | DES ML | 已评估 | 保留为监督学习/候选生成参考，不计入 AL 复现 |
