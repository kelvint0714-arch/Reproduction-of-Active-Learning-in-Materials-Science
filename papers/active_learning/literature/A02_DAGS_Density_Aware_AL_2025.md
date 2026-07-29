# A02｜DAGS：面向非均匀材料设计空间的密度感知主动学习

## 论文信息

- **正式题名**：*Density-aware active learning for materials discovery: a case study on functionalized nanoporous materials*
- **作者**：Vassilis Gkatsis, Petros Maratos, Christos Rekatsinas, George Giannakopoulos, Panagiotis Krokidas
- **年份 / 期刊**：2025，*Physical Chemistry Chemical Physics* 27, 23152–23165
- **DOI / 全文**：[10.1039/D5CP02908B](https://doi.org/10.1039/D5CP02908B)
- **HTML 全文**：[RSC Publishing](https://pubs.rsc.org/en/content/articlehtml/2025/cp/d5cp02908b)

## 这篇论文解决什么问题

普通的距离型主动学习容易过度选择稀疏区域和离群点。在真实材料设计空间中，候选点往往分布很不均匀，因此“离已标注点最远”并不一定等于“最值得标注”。

DAGS（Density-Aware Greedy Sampling）在 iGS 的输入—输出空间探索分数上加入局部数据密度权重，使新样本同时具有信息性和代表性。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 在有限标注预算下，用更少样本训练出低误差的材料性质回归模型 |
| **输入** | 合成函数特征；真实任务使用功能化纳米多孔材料的数值描述符 |
| **标签 / oracle** | 真实数据任务包括 MOF 中 O₂、N₂、CH₄、H₂、He 的扩散相关目标值 |
| **代理模型** | XGBoost regressor |
| **采集策略** | DAGS：iGS 分数乘以由 K 近邻欧氏距离得到的局部密度权重 |
| **对照方法** | Random、iGS、Query-by-Committee、Regression Tree-based AL |
| **单轮动作** | 训练 XGBoost，计算未标注点的 iGS 与密度分数，选择乘积最大的点查询标签 |

## 怎样评价

- 测试集 MAE 随查询次数的变化；
- 达到同一 MAE 所需的 oracle 查询数；
- 10 次重复实验的平均曲线；
- 在均匀 / 非均匀合成空间，以及多个真实纳米多孔材料数据集上的稳健性。

论文也报告了边界：DAGS 在五个真实设计空间中的四个表现更好；在较小的 He 数据空间里，偏探索的 iGS 更优。因此密度权重不是对所有数据都必然占优。

## 代码与数据核验

- **作者代码（论文指定 v1.0.0）**：[insane-group/Density_Aware_Greedy_Sampling](https://github.com/insane-group/Density_Aware_Greedy_Sampling)
- **O₂ / N₂ 数据**：[ibarisorhan/MOF-O2N2](https://github.com/ibarisorhan/MOF-O2N2/blob/main/mofScripts/MOFdata.csv)
- **CH₄ / H₂ / He 数据**：[hdaglar/MOF-basedMMMs_ML](https://github.com/hdaglar/MOF-basedMMMs_ML/blob/main/rawdata.zip)
- **补充信息**：[RSC supplementary information](https://www.rsc.org/suppdata/d5/cp/d5cp02908b/d5cp02908b1.pdf)
- **核验状态（2026-07-29）**：论文的数据可用性段明确给出代码版本、代码仓库和两组数据来源；仓库提供环境脚本、合成数据生成器和命令行入口。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

DAGS 优化的是代理模型在设计空间上的整体预测质量和标注效率。它没有用 EI、PI、UCB 去寻找最大性能材料，也没有把“当前最好性质”写进采集目标。

## 复现建议

- **难度**：低到中等，是本仓库优先级最高的复现对象之一。
- **最小任务**：
  1. 先运行仓库自动生成的一个均匀和一个非均匀合成数据集；
  2. 比较 `random`、`igs`、`dags` 三种方法；
  3. 固定 5 个初始点、150 次总查询和 10 次重复，画 MAE 曲线；
  4. 再下载 O₂ 数据，只运行一个真实材料任务；
  5. 检查 DAGS 是否在非均匀空间优于 iGS，而不是只报告最终 MAE。
