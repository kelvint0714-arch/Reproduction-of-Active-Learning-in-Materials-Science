# A06｜RT-AL：为 MOF 性质预测主动构造小训练集

## 论文信息

- **正式题名**：*Informative Training Data for Efficient Property Prediction in Metal–Organic Frameworks by Active Learning*
- **作者**：Ashna Jose, Emilie Devijver, Noel Jakse, Roberta Poloni
- **年份 / 期刊**：2024，*Journal of the American Chemical Society* 146, 6134–6144
- **DOI / 论文页**：[10.1021/jacs.3c13687](https://doi.org/10.1021/jacs.3c13687)
- **开放预印本**：[ChemRxiv 10.26434/chemrxiv-2023-sw9kv](https://doi.org/10.26434/chemrxiv-2023-sw9kv)

## 这篇论文解决什么问题

MOF 的带隙和吸附性质可能需要昂贵计算。论文提出 Regression Tree-based Active Learning（RT-AL），从大候选池中挑选少量多样、代表且信息量高的 MOF 建立训练集，再训练性质回归器。

其重点不是找到单个最高吸附量 MOF，而是在标签分布不均衡时仍用较小训练集准确预测整个测试集。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 降低 MOF 性质回归的标注成本，同时保持测试集预测质量 |
| **输入** | QMOF、hMOF、dMOF 的低维化学计量与几何描述符 |
| **标签 / oracle** | MOF 带隙，以及 CO₂ / CH₄ 等气体吸附性质 |
| **采样模型** | 标准 regression tree 对已标注特征—标签空间进行分区 |
| **性质代理模型** | 论文实验使用由主动学习子集训练的 Random Forest 回归器 |
| **采集策略** | 根据树叶中的响应方差、未标注样本分布及代表性分配新标签；并研究加入多样性 / 代表性准则的变体 |
| **对照方法** | Random sampling 及其他模型无关或模型相关的 AL 方法 |

## 怎样评价

- 固定测试集 MAE 随训练集大小变化；
- 多次运行的平均误差和方差；
- 与随机采样及其他 AL 方法在相同标签预算下比较；
- 不同描述符和不平衡标签分布下的稳定性。

## 代码与数据核验

- **作者代码**：[AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs](https://github.com/AshnaJose/Regression-Tree-based-Active-Learning-for-MOFs)
- **数据、描述符、选中训练集和基准 MAE**：[Zenodo 10.5281/zenodo.10511345](https://doi.org/10.5281/zenodo.10511345)
- **核验状态（2026-07-29）**：Zenodo 明确关联 JACS 论文，并指向代码仓库；压缩数据约 4.1 GB，下载和预处理成本不可忽略。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

论文以测试集 MAE 和小训练集代表性为目标，不使用 EI / UCB 去最大化吸附量或带隙。即使标签包含气体吸附性能，任务也仍是“学准整张性质映射”。

## 复现建议

- **难度**：中到高；算法本身不复杂，主要负担是 4.1 GB 数据和多套描述符。
- **最小任务**：
  1. 先运行代码仓库提供的 RT-AL 最小示例；
  2. 只取一套已计算描述符和一个目标，例如 QMOF band gap；
  3. 固定测试集，比较 RT-AL 与 Random；
  4. 用 20、40、60、80、100 个训练样本画 MAE 曲线；
  5. 检查重复运行方差，而不只比较一次结果；
  6. 最后再加入第二种描述符，观察低数据阶段的表征敏感性。
