# A08｜AIPHAD：用主动学习构建和理解材料相图

## 论文信息

- **正式题名**：*AIPHAD, an active learning web application for visual understanding of phase diagrams*
- **作者**：Ryo Tamura, Haruhiko Morito, Guillaume Deffrennes, Masanobu Naito, Yoshitaro Nose, Taichi Abe, Kei Terayama
- **年份 / 期刊**：2024，*Communications Materials* 5, 139
- **DOI / 全文**：[10.1038/s43246-024-00580-7](https://doi.org/10.1038/s43246-024-00580-7)
- **NIMS 数据记录**：[MDR dataset record](https://mdr.nims.go.jp/datasets/1473a8e6-5355-4091-bb8a-ab059bb6ed17)

## 这篇论文解决什么问题

相图包含多个离散相区，逐点实验成本很高。AIPHAD 把 PDC（Phase Diagram Construction）算法做成网页和 Python 工具：根据已知相标签估计未测点所属相的概率，再选择最不确定的位置做下一次实验。

论文用 Fe–Ti–Sn 三元体系演示真实材料实验，并借助新实验逐步澄清相边界和 Heusler 相区域。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 用尽量少的实验补全相图和澄清相边界 |
| **输入** | 离散化的成分、温度或其他相图坐标；工具支持一般多维候选点 |
| **标签 / oracle** | 各实验点的离散相类别；未标注点在 Python 接口中记为 `-1` |
| **代理模型** | RBF 图上的 Label Propagation 或 Label Spreading |
| **采集策略** | Least Confidence、Margin Sampling、Entropy Approach；Random 作为选择项 |
| **批量策略** | 按不确定性排序，或用 Neighbor Exclusion 避免批次候选过于相邻 |
| **真实 oracle** | 样品制备后通过 XRD 等实验识别相类别 |

## 怎样评价

论文的真实实验演示主要观察：

- 不确定性图与估计相图如何随新实验更新；
- 新实验是否澄清相边界；
- 已知相区和目标 Heusler 相区域是否被正确识别；
- 需要提出和执行多少个新实验。

**重要限制**：论文的 Fe–Ti–Sn 演示没有给出一个统一的固定测试集分类指标作为主结果。因此复现时应自行增加 held-out accuracy、macro-F1、边界误差或相图像素一致率，不能把可视化效果当成唯一评价。

## 代码与数据核验

- **Python 代码**：[NIMS-DA/aiphad](https://github.com/NIMS-DA/aiphad)
- **官方文档**：[AIPHAD 1.0.0 documentation](https://nims-da.github.io/aiphad/docs/en/index.html)
- **Web 应用**：[aiphad.org](https://aiphad.org/)
- **论文数据**：正文说明所有研究数据包含在论文及 Supplementary Data 1–5 中。
- **核验状态（2026-07-29）**：论文 Code availability 明确给出 GitHub 和文档地址；包可通过 `pip install aiphad` 安装。网页服务是否长期在线需要运行时单独检查，Python 版本更适合作为可追踪复现入口。

## AL 还是 BO

**判定：真正的主动学习，不是贝叶斯优化。**

它要提高整个相图分类和边界知识，而不是最大化某项连续材料性能。论文后段可以按某一相的预测概率帮助定向寻找该相，但核心 PDC 循环仍是不确定性采样的相图学习。

## 复现建议

- **难度**：软件回放低，真实材料实验高。
- **最小任务**：
  1. 使用文档中的低维相图示例或 Supplementary Data；
  2. 隐藏大部分已有相标签，把完整数据当作离线 oracle；
  3. 比较 LC、MS、EA、Random 四种选择；
  4. 每轮揭示一个标签并重训；
  5. 记录 macro-F1、相边界附近准确率和达到目标准确率所需实验数；
  6. 最后再尝试多点批量建议与 Neighbor Exclusion。
