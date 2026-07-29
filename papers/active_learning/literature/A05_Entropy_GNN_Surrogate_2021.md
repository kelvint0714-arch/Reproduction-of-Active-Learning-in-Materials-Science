# A05｜GNN 表征 + Gaussian Process 的熵主动学习

## 论文信息

- **正式题名**：*Entropy-based Active Learning of Graph Neural Network Surrogate Models for Materials Properties*
- **作者**：Johannes Allotey, Keith T. Butler, Jeyan Thiyagalingam
- **年份 / 期刊**：2021，*The Journal of Chemical Physics* 155, 174116
- **DOI**：[10.1063/5.0065694](https://doi.org/10.1063/5.0065694)
- **开放预印本**：[arXiv:2108.02077](https://arxiv.org/abs/2108.02077)

## 这篇论文解决什么问题

晶体 GNN 预测准确，但通常需要大量 DFT 标签。论文把 MEGNet 学到的晶体结构嵌入作为 Gaussian Process 的输入，让模型既能预测形成能，又能给出可用于主动学习的预测不确定性。

主动学习的目标是优先标注模型最不确定的材料，使固定测试集上的形成能预测误差比随机加标签下降得更快。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 用更少 DFT 标签提高整个候选空间上的形成能代理模型精度 |
| **输入** | Materials Project 中氧化物的晶体结构 |
| **标签 / oracle** | DFT 形成能（每原子） |
| **代理模型** | MEGNet 生成结构潜在向量，再由使用 Laplacian kernel 的 Gaussian Process 回归；论文称 CFGP |
| **采集策略** | 根据 GP 预测分布的熵 / 不确定性选择下一批待标注材料 |
| **对照方法** | Random sampling |
| **测试集** | 与主动学习候选池隔离的 1,460 个材料 |

## 怎样评价

- 固定测试集 MAE 随新增标签数的变化；
- 随机采样与熵采样学习速率；
- 最终测试集 MAE、MSE 和 \(R^2\)；
- 预测区间校准和残差—不确定性关系；
- 多次主动学习运行的均值与标准差。

论文报告熵采样可使测试性能随新标签改善的速度约为随机采样的两倍。这个结论针对论文数据、模型与预算，不应直接外推到所有材料数据。

## 代码与数据核验

- **作者代码**：[keeeto/gp-net](https://github.com/keeeto/gp-net)
- **完整数据、保存模型和论文实验包**：[Zenodo 10.5281/zenodo.4922828](https://doi.org/10.5281/zenodo.4922828)
- **Zenodo 内容**：Materials Project 形成能数据、已训练 MEGNet 模型、GP 预测、随机 / 熵采样 MAE 结果、潜在向量和绘图 notebook。
- **核验状态（2026-07-29）**：Zenodo 明确给出重建论文实验的命令和代码仓库；实验包约 222 MB。代码依赖的是较旧的 TensorFlow / MEGNet 环境，不能假定在最新 Python 上直接运行。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

采集只关注模型不知道什么，评价是固定测试集的全局形成能误差；算法不寻找形成能最高或最低的材料。

## 复现建议

- **难度**：高；概念清晰，但原始深度学习环境较旧。
- **最小任务**：
  1. 不先重训 MEGNet；
  2. 下载 Zenodo 已提供的潜在向量、真实标签和保存结果；
  3. 在固定潜在空间上重放 GP 的 Random 与 entropy 两种采样；
  4. 复现 MAE—标签数曲线；
  5. 流程稳定后，再尝试恢复 `gp-megnet.yml` 环境并重训结构编码器。

这样能把“GNN 学表示”和“GP 提供不确定性”分成两步理解。
