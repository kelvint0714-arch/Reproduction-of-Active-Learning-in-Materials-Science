# PS01｜聚合物太阳能电池：NLP 数据构建与目标导向顺序选样

## 论文与资源

- **正式题名**：*Accelerating Materials Discovery for Polymer Solar Cells: Data-Driven Insights Enabled by Natural Language Processing*
- **作者**：Pranav Shetty, Aishat Adeboye, Sonakshi Gupta, Chao Zhang, Rampi Ramprasad
- **期刊 / 年份**：*Chemistry of Materials* 36, 7676–7689 (2024)
- **DOI**：[10.1021/acs.chemmater.4c00709](https://doi.org/10.1021/acs.chemmater.4c00709)
- **作者代码与数据**：[pranav-s/PolymerSolarCellsML](https://github.com/pranav-s/PolymerSolarCellsML)，MIT
- **本仓库状态**：`未开始`

## 这篇论文真正做了什么

作者先用 NLP 从约 20 年的聚合物太阳能电池文献中抽取器件数据，再人工整理一部分数据并补充供体、受体的 SMILES/结构指纹。监督模型预测功率转换效率（PCE），顺序选样模拟则比较怎样更快找到高 PCE 的供体—受体组合。

论文和代码包含 GP-UCB、GP-PI、GP-EI、Greedy、GP-Thompson Sampling、线性 contextual bandit 和 Random 等策略。论文实际优化的是**单一指标 PCE**；多目标优化只是未来方向，不能写成论文已经完成了多目标主动学习。

## 为什么不归入 `AL-core`

作者使用 active learning 术语，但循环的主要目标是尽快发现高 PCE 候选，采集函数和结果也以性质极值为中心。因此本仓库将它标为：

```text
目标导向 AL / BO / contextual bandit 混合应用
```

它不是以固定测试集整体误差下降为唯一目标的模型学习型 AL。论文关于“加快研究进程”的结论来自历史数据上的回顾性模拟，不等于真实自动实验室已经节省了相同时间。

## 数据和算法映射

| 模块 | 论文中的内容 |
|---|---|
| 输入 | 供体—受体组合、结构指纹及器件/实验条件 |
| 标签 | 功率转换效率 PCE |
| 数据来源 | NLP 抽取数据＋人工整理数据 |
| 代理模型 | 以 GPR 为主的 PCE 模型；另有 contextual bandit |
| 采集策略 | UCB、PI、EI、Greedy、TS、bandit、Random |
| Oracle | 离线回放时从历史文献数据揭示 PCE |
| 主要目标 | 用更少选择步骤找到高 PCE 组合 |

## 公开资产与复现边界

仓库包含：

- NLP 抽取数据和人工整理数据；
- 供体/受体结构指纹及名称标准化元数据；
- 顺序选样代码和 NLP 评价代码；
- `environment.yml`，指定 Python 3.10、RDKit 2023.9.4 和 scikit-learn 1.3.2；
- MIT 许可证。

这使它成为当前较完整的聚合物目标优化复现案例。不过历史文献数据可能有测量条件差异、发表偏差和时间泄漏，复现时必须保留按年份回放的设置，不能随意随机打乱后声称模拟了真实发现过程。

## 最小复现建议

1. 固定作者仓库 commit 和环境。
2. 先运行监督 PCE 预测，检查结构指纹、缺失值和划分。
3. 只比较 Random、Greedy、GP-UCB、GP-EI 四种策略。
4. 使用相同初始供体—受体组合、预算和随机种子。
5. 同时报告 best-so-far、找到 top 1% 所需次数和测试 MAE。
6. 再加入 contextual bandit，解释它与 GP 采集函数的差异。
7. 逐步检查时间回放是否使用了当时不可能获得的未来信息。

## 对本项目的价值

价值很高，但应放在基础 AL/BO 复现之后。它的“供体＋受体＋工艺条件 → 性能”结构与未来粘合剂的“树脂＋固化剂＋配方/固化条件 → 性能”非常接近，可用于设计组合材料的数据适配器、候选池和离线回放协议。
