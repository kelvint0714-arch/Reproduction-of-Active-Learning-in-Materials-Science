# A07｜UQALE：分子性质模型的 OOD 不确定性与主动学习

## 论文信息

- **正式题名**：*Evaluating uncertainty-based active learning for accelerating the generalization of molecular property prediction*
- **作者**：Tianzhixi Yin, Gihan Panapitiya, Elizabeth D. Coda, Emily G. Saldanha
- **年份 / 期刊**：2023，*Journal of Cheminformatics* 15, 105
- **DOI / 全文**：[10.1186/s13321-023-00753-5](https://doi.org/10.1186/s13321-023-00753-5)
- **PNNL 项目页**：[Pacific Northwest National Laboratory](https://www.pnnl.gov/publications/evaluating-uncertainty-based-active-learning-accelerating-generalization-molecular)

## 这篇论文解决什么问题

分子性质模型可能在训练分布内表现很好，却无法推广到训练集中缺失的新分子类型。论文先系统评价多种不确定性量化方法，再把其中的方法用于主动选样，检验它们能否比随机采样更快补齐人为构造的 OOD 区域。

它的重要性在于给出负面但真实的结果：不确定性指导的 AL 相比随机采样有统计显著但幅度较小的改善，当前方法并没有自动解决小数据问题。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 更快提高对未覆盖分子类型的泛化能力，而不是寻找性质极值 |
| **输入** | 分子结构的数值描述符，或用于图神经网络的分子图 |
| **标签 / oracle** | 水溶解度和氧化还原电位 |
| **代理模型** | Molecular Descriptor Model（全连接神经网络）和 Graph Neural Network |
| **不确定性方法** | 深度学习 UQ 方法与基于数据密度 / 近邻的估计；没有单一方法在所有指标上最好 |
| **采集策略** | 按不确定性线性加权抽样；越不确定的分子被选中概率越高 |
| **OOD 设置** | 沿前三个 PCA 方向分箱，每次从初始训练集移除一个分箱来模拟缺失分子类型 |

原论文的主要 AL 检验采用一次批量采集，重点评价新批次是否补入 OOD 分子及其即时泛化收益，而不是长轮次闭环。

## 怎样评价

- 新增 AL 批次相对随机批次带来的 RMSE 百分比改善；
- OOD 分箱、其余 ID 分箱和全测试集上的分别表现；
- AL 所选批次中 OOD 分子的比例；
- ENCE、误差相关性、OOD 检出相关性等 UQ 指标；
- 多种初始训练比例、批量大小及 30 次重复。

## 代码与数据核验

- **作者代码**：[pnnl/UQALE](https://github.com/pnnl/UQALE)
- **水溶解度数据**：[Figshare 10.6084/m9.figshare.14552697](https://doi.org/10.6084/m9.figshare.14552697)
- **氧化还原电位数据**：[piyushtagade/SLAMDUNCS](https://github.com/piyushtagade/SLAMDUNCS)
- **后续 OOD AL 数据归档**：[Zenodo 10.5281/zenodo.13769710](https://doi.org/10.5281/zenodo.13769710)
- **核验状态（2026-07-29）**：论文 Data availability 明确列出 UQALE 代码和两项原始数据来源；后续 Zenodo 归档提供 OOD 主动学习数据。不同目录可能对应原论文与后续扩展，复现时要记录所用提交和数据版本。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

算法选择的是能补足模型知识盲区的分子，评价 OOD / ID RMSE；它没有寻找溶解度或氧化还原电位的最大值。

## 复现建议

- **难度**：中到高；实验组合很多，但可裁剪。
- **最小任务**：
  1. 只使用水溶解度数据和 Molecular Descriptor Model；
  2. 沿第一主成分分成 5 箱，移除其中 1 箱；
  3. 比较 Random 与最近邻密度引导的一个 AL 批次；
  4. 固定一个初始比例和一个批量大小；
  5. 先跑 5 个种子，再扩展到论文的 30 次；
  6. 同时报告 OOD RMSE 和全测试集 RMSE，避免只展示有利指标。
