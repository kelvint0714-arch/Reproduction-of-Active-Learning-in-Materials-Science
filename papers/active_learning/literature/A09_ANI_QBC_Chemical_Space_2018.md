# A09｜ANI-1x：QBC 主动覆盖分子化学空间

## 论文信息

- **正式题名**：*Less is more: Sampling chemical space with active learning*
- **作者**：Justin S. Smith, Ben Nebgen, Nicholas Lubbers, Olexandr Isayev,
  Adrian E. Roitberg
- **年份 / 期刊**：2018，*The Journal of Chemical Physics* 148, 241733
- **DOI**：[10.1063/1.5023802](https://doi.org/10.1063/1.5023802)
- **开放预印本**：[arXiv:1801.09319](https://arxiv.org/abs/1801.09319)
- **本仓库核验日期**：2026-08-03

## 为什么补入这篇基础工作

2026 年新发表的铈氢化物势函数论文直接沿用这篇论文的 Query by Committee（QBC）
数据生成思路。原清单已有 DP-GEN、ALEBREW、FLARE 等材料势函数分支，却遗漏了
ANI-1x 这条“模型委员会分歧 → 查询量化标签 → 扩充势能面覆盖”的早期代表路线。

论文不是寻找能量最低的分子，也不是用 EI/UCB 做极值优化。它试图用更少的量化化学
标签学习更广的 CHNO 分子构象空间，使能量和力模型在独立 COMP6 基准上更准确。

## 主动学习要素

| 要素 | 论文中的设置 |
|---|---|
| **AL 目标** | 自动发现现有 ANI 势函数预测不可靠的化学/构象区域，提高全局能量与力精度和可迁移性 |
| **输入** | CHNO 分子的原子种类、三维坐标与原子环境描述 |
| **标签 / oracle** | 量化化学计算得到的分子能量和原子力 |
| **代理模型** | 多个独立训练的 ANI（ANAKIN-ME）原子神经网络势 |
| **不确定性** | committee 成员对同一构型预测的分歧 |
| **查询策略** | QBC：从构象、分子动力学和化学空间采样产生的候选中选择高分歧构型做新量化标注 |
| **评价** | COMP6 上总能量、相对能量和力的 MAE/RMSE；不同 AL 数据比例下的标签效率 |

论文报告 AL 模型只使用原 ANI-1 数据规模的 10% 时即可达到 ANI-1 的 COMP6 水平，
使用约 25% 时明显优于 ANI-1。这里的比例和结论只适用于论文定义的数据生成、模型和
COMP6；不能外推成“任何任务都能节省 75% 标签”。

## 代码、数据与许可证核验

- **COMP6 基准**：[isayev/COMP6](https://github.com/isayev/COMP6)，MIT；仓库明确
  给出 ANI-1/ANI-1x 的能量、相对能量和力 MAE/RMSE。
- **ANI-1x 数据**：[Figshare 10.6084/m9.figshare.10047041.v1](https://doi.org/10.6084/m9.figshare.10047041.v1)，
  CC0；v1 文件 `ani1x-release.h5` 为 5,590,846,027 bytes，MD5
  `98090dd6679106da861f52bed825ffb7`。
- **数据读取代码**：[aiqm/ANI1x_datasets](https://github.com/aiqm/ANI1x_datasets)，MIT。
- **论文时代模型接口**：[isayev/ASE_ANI](https://github.com/isayev/ASE_ANI)，MIT；
  上游已标记 deprecated，要求 Python 3.6、CUDA 9.2 和 Linux/NVIDIA 环境。
- **现代官方实现**：[aiqm/torchani](https://github.com/aiqm/torchani)，MIT；可用于
  当前机器上的 ANI-1x 推理 smoke，但不能把现代实现结果冒充 2018 年训练环境。
- **未核验**：没有找到能够一键重跑论文全部分子生成、QBC 阈值、量化计算和每轮
  重训的固定 release/tag。公开预训练模型和数据足以回放评估，但不足以声称完整
  忠实复现 AL 数据生成全过程。

## AL 还是 BO

**判定：真正的模型学习型主动学习。**

查询信号是模型委员会对势能/力的分歧，目标是覆盖势能面并降低独立基准误差；没有
以 best-so-far、top-k、regret 或 Pareto 前沿作为主要目标。

## 最小复现任务

1. 不下载完整 5.59 GB ANI-1x，先克隆 MIT 许可的 COMP6，并固定一个小子集；
2. 用现代官方 TorchANI 在 CPU/MPS 上加载 ANI-1x，对固定子集计算总能量、相对
   能量和力误差；
3. 将误差定义、单位和聚合方式与 COMP6 README/论文一致，不能把每分子误差改成
   每原子误差；
4. 把这一步标为“预训练模型评估 smoke”，不标为 AL 循环复现；
5. 随后在同一小候选池和标签预算下重实现 Random 与 committee disagreement，
   比较固定测试集学习曲线，作为统一协议重实现。

完整论文复现需要恢复旧 ANI/量化计算流程、全部采样器和每轮数据版本，计算与环境
成本较高，因此优先级低于 A01/A02，但应先于复杂材料势函数闭环用于理解 QBC。
