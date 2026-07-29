# A01｜微结构—性能映射中的主动学习：采样与表征同样重要

## 论文信息

- **正式题名**：*Active learning for regression of structure–property mapping: the importance of sampling and representation*
- **作者**：Hao Liu, Berkay Yucel, Baskar Ganapathysubramanian, Surya R. Kalidindi, Daniel Wheeler, Olga Wodo
- **年份 / 期刊**：2024，*Digital Discovery* 3, 1997–2009
- **DOI**：[10.1039/D4DD00073K](https://doi.org/10.1039/D4DD00073K)
- **官方论文页**：[NIST publication page](https://www.nist.gov/publications/active-learning-regression-structure-property-mapping-importance-sampling-and)

## 这篇论文解决什么问题

论文不是寻找“性能最高的一个材料”，而是从一个已有微结构库中，用尽量少的昂贵物理计算标签，训练出在整个微结构空间都足够准确的结构—性能回归模型。

它同时研究两个变量：

1. 选哪些样本去标注；
2. 怎样把微结构表示成机器学习可以使用的特征。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 用最少的性能评估构建可靠的微结构—性能映射 |
| **输入** | 二维或三维二相微结构；再转换为图描述符，或两点相关函数经 PCA 得到的低维表示 |
| **标签 / oracle** | 有机光伏微结构的短路电流 \(J_{sc}\)；二维和三维复合材料微结构的有效刚度 \(C_{11}^{eff}\)，均由物理模型计算 |
| **代理模型** | Gaussian Process Regression；论文使用 Matérn 核和零均值函数 |
| **采集策略** | 最大预测方差、GSx、GSy、iGS；随机采样作为基线 |
| **单轮动作** | 选择一个未标注微结构，由物理模型计算其性能，加入训练集并重训 GP |

## 怎样评价

- 测试集 MAE 随已标注样本数的学习曲线；
- 达到“从初始误差到全数据最优误差的 80% 改善”所需样本数；
- 所选子集与全集之间的 Wasserstein 距离；
- 所选微结构分布的熵；
- 未标注池上的平均预测不确定性；
- 20 次重复实验的均值与标准差。

论文的核心结论是：在其三个微结构数据集中，合理的表征与主动采样结合后，约 5% 的微结构性能评估即可形成稳健映射；但最佳采样策略会随任务和维度变化，不能只凭算法名称预先断定。

## 代码与数据核验

- **NIST 代码与二维/三维弹性数据**：[usnistgov/active-learning](https://github.com/usnistgov/active-learning)
- **OPV 工作流代码**：[hliu56/Active-Learning-Using-various-representations](https://github.com/hliu56/Active-Learning-Using-various-representations)
- **相关归档**：[Zenodo 10.5281/zenodo.7562957](https://doi.org/10.5281/zenodo.7562957)
- **核验状态（2026-07-29）**：论文正文的数据可用性声明列出了上述两个 GitHub 仓库；弹性数据文件和运行依赖随 NIST 仓库提供。未在本卡中承诺所有历史环境可不经修改直接运行。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

目标函数是降低整个输入空间上的预测误差和标注成本；算法不会因为某个样本的性能值更大就优先寻找它。iGS 使用输出空间距离，但仍是为了获得覆盖良好的训练集，而不是最大化 \(J_{sc}\) 或刚度。

## 复现建议

- **难度**：中等。
- **最小任务**：
  1. 只使用 NIST 仓库中的二维弹性数据；
  2. 固定一个训练 / 测试划分；
  3. 比较 Random、最大方差、iGS 三条 MAE—样本数曲线；
  4. 先运行 5 个随机种子确认流程，再扩展到论文的 20 次重复；
  5. 最后再比较“描述符”和“两点相关函数 + PCA”两种输入表示。

这样可以先复现主动学习主循环，再逐步加入微结构表征这一材料科学特有环节。
