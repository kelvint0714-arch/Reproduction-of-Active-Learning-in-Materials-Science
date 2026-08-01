# 2026 观察论文：为什么暂不进入复现清单

更新日期：2026-07-31。

本页覆盖 `papers/LITERATURE_WATCH.md` 中尚未获得正式 ID 的四篇观察论文。它们没有
被漏掉；当前证据不足以写成可执行 recipe。先写清阻塞，胜过编造代码入口、数据或
运行结果。

| 临时标识 | 论文 | 当前判断 | 进入 manifest 前必须补齐 |
|---|---|---|---|
| OBS-PARETO | [Active learning enables generation of molecules that advance the known Pareto front](https://doi.org/10.1038/s41524-025-01924-8) | 生成模型＋多目标优化/AL 混合 | 作者代码、训练/Oracle 数据、许可证、论文图对应入口、多目标评价定义 |
| OBS-DISCOVERY | [Discovery Learning predicts battery cycle life from minimal experiments](https://doi.org/10.1038/s41586-025-09951-7) | 物理引导、小样本与实验设计混合 | 正式代码、可公开工业数据范围、AL 循环和消融、可运行的离线 Oracle |
| OBS-RAFFLE | [RAFFLE: active learning accelerated interface structure prediction](https://doi.org/10.1038/s41524-025-01749-5) | 结构搜索＋主动扩充能量标签 | 官方代码入口、版本/许可证、标签计算后端、全局模型学习与低能结构优化的边界 |
| OBS-QUANTUM | [Quantum-Inspired Active Learning for Accelerated Materials Discovery](https://doi.org/10.1109/NQComp68334.2026.11497667) | 合成数据上的 quantum-inspired 查询策略 | 论文—仓库版本映射、真实材料数据对应、引用核验、凭据清理与可审计基线 |

## 准入操作

每篇按以下顺序处理：

1. 从出版社 DOI 页面核对题名、作者、版本和数据/代码声明；
2. 只接受作者、机构或论文直接链接的官方仓库/归档；
3. 核对许可证、release/tag/commit、数据 DOI、文件哈希和最小入口；
4. 明确它学习整个映射、寻找最优、生成候选，还是几者的混合；
5. 找到可隐藏标签的离线候选池或可实际调用的 Oracle；
6. 确认 Random/Greedy 等基线和论文主指标能够从公开产物重算；
7. 分配稳定 ID、建立论文卡和 recipe，再加入 `manifest.json`。

## 停止条件

若代码或关键数据未公开、许可证不允许使用、论文任务与仓库数据无法对应，或完整
流程依赖不可获得的工业/实验接口，则维持观察状态。此时可以阅读方法，但不得写
`recipe-ready`，更不得写 `completed`。
