# P05｜DKL-on-STM：神经网络表示 + GP + UCB

## 论文与资源

- 论文：[Uncovering multiscale structure-property correlations via active learning in scanning tunneling microscopy](https://doi.org/10.1038/s41524-025-01642-1)
- 期刊：npj Computational Materials 11, 189 (2025)
- 作者代码与数据：[gnganesh99/DKL_on_STM](https://github.com/gnganesh99/DKL_on_STM)
- 本仓库状态：`未开始`

## 这篇论文做了什么

论文用深核学习（DKL）连接显微结构图像与局部测量目标：

```text
局部图像/结构片段
  → 深度神经网络压缩成低维表示
  → GP 在表示空间做概率回归
  → 输出预测均值与方差
  → UCB 选择下一测量位置
```

这是“机器学习结合传统神经网络”的一个清晰模式：DNN 负责表示，GP 负责概率预测和不确定性，UCB 负责主动选择。

论文研究 EuZn₂As₂：从 512×512 STM 形貌图提取 30×30 patch，学习局部结构与 \(dI/dV\) 光谱派生标量（例如带隙或特定能区电导指标）之间的关系。作者工作流中的编码器结构为 `64 → 64 → 2`，二维表示再进入 RBF-GP；具体 epoch 和采集参数必须以锁定后的论文代码为准。

## 主动学习映射

| 模块 | 本论文中的内容 |
|---|---|
| 输入 | STM 图像中的局部结构片段 |
| 目标 | 从局部 \(dI/dV\) 光谱计算出的 scalar 性质 |
| 表示 | DNN embedding |
| 代理模型 | embedding 上的 GP，即 DKL |
| 不确定性 | GP 后验方差 |
| 采集函数 | UCB |
| Oracle | STM 测量；模拟复现时由公开数据查询替代 |
| 输出 | 下一测量坐标与更新后的结构—性质关系 |

## 公开资产与缺口

作者仓库包含数据、GPax 工作流、`Workflow_DKL_STM.ipynb` 模拟 Notebook 和仪器接口相关内容。模拟闭环可先于真实设备控制复现。

主要限制：

- 真实 STM 控制依赖 LabVIEW/仪器环境；
- 当前 GPax 与论文时版本可能不同；
- 图像预处理、patch 尺寸、DNN 结构和 UCB 参数需从代码与论文共同核对；
- 模拟工作流成功不代表真实仪器闭环已复现。

模拟复现难度为**中高**，真实仪器复现难度为**极高**。

## 忠实复现步骤

1. 固定论文、数据和作者仓库 commit。
2. 在独立环境中先运行 `Workflow_DKL_STM.ipynb`。
3. 确认输入 patch、scalar target、训练集和未测量坐标。
4. 保存 DNN embedding、GP 均值/方差和每轮 UCB 分数。
5. 复现下一坐标选择和标签回填。
6. 用相同预算比较 Random、普通 GP 和 DKL。
7. 核对论文图表与结构—性质相关性，不连接真实仪器。
8. 记录未来把图像换成材料描述符或分子 embedding 所需接口。

## 学习时必须回答

- 为什么不直接让 DNN 输出最终标量？
- DNN embedding 与手工描述符有什么区别？
- GP 在低维 embedding 上为什么更容易工作？
- DKL 的不确定性是否会被过度灵活的表示扭曲？
- UCB 中 \(\beta\) 如何改变探索与利用？

## 对本项目的价值

价值非常高。它直接展示神经网络与概率模型怎样分工，也是以后 `GNN embedding + GP + UCB` 的结构原型。
