# 论文复现路线

路线按“真正的模型学习型 AL → 通用基准 → GNN/不确定性 → 相图与势函数 → 真实材料应用”推进。贝叶斯优化单独作为副线，不再占用主动学习 R1。

逐篇可执行路径集中在 [recipes 索引](recipes/README.md)。本路线图决定执行顺序，
recipe 决定具体来源、环境、命令、指标和证据交付；两者都不代表已经复现成功。

## R0：先建立判定能力

阅读：

1. [主动学习与贝叶斯优化的边界](../docs/04_主动学习与贝叶斯优化的边界.md)；
2. [查询策略与采集函数的数学结构](../docs/05_查询策略与采集函数数学结构.md)；
3. [统一主动学习流程](../docs/02_统一主动学习流程.md)；
4. [持续文献清单](../papers/LITERATURE_WATCH.md)。

完成标准：

- 能解释为什么 P01 是 BO；
- 能说清 AL 的主要目标是全局模型/数据覆盖，BO 的主要目标是极值；
- 能分别列出两者的评价指标；
- 读一篇新论文时，能根据目标和指标分类，而不是只看标题。

## R1：A01 NIST 微结构—性质主动学习

目标：

- 跑通真正的回归主动学习循环；
- 比较 Random、最大方差和 iGS；
- 理解材料表示与查询策略是两个独立变量；
- 用固定测试集 MAE 和标签效率判断效果。

最低完成标准：

- 使用作者公开的二维弹性预计算数据；
- 锁定论文 DOI、上游 commit、数据文件和环境；
- 固定同一初始集、测试集和至少 5 个随机种子；
- 输出 MAE—已标注样本数学习曲线；
- 解释采集方法为什么不是在找最大刚度；
- 记录与论文趋势相符、部分相符或不相符。

操作见 [START_HERE](START_HERE.md)。

## R2：A02 DAGS 密度感知主动学习

目标：

- 在合成数据上比较 Random、iGS、QBC、RT-AL 和 DAGS；
- 理解“最远/最不确定”可能过度选择离群点；
- 检验密度权重在均匀与非均匀候选池中的作用；
- 再迁移到一个 MOF 气体扩散任务。

最低完成标准：

- 先跑仓库自动生成的合成数据，不先下载全部材料数据；
- 固定相同初始点、查询预算和重复次数；
- 输出测试 MAE 学习曲线及均值/标准差；
- 至少做一个 `DAGS 去掉密度权重` 的消融；
- 记录论文报告的失败/不占优情形，而不只展示最好结果。

## R3：通用材料 AL 基准

### R3A：材料数据冗余与 QBC

使用 `paper-data-redundancy` 的一个数据库×一个性质，比较：

- Random；
- RF uncertainty；
- XGBoost uncertainty；
- RF–XGBoost committee disagreement。

完成标准：报告相同测试误差所需标签比例，并区分 ID 与 OOD 表现。

### R3B：A03 Benchmark-AL-Mat

先选一个小型数据集，只比较 Random、Tree-based-R、RD-GS：

- 缩小 AutoML 单轮预算只是 smoke test；
- 正式结果恢复论文预算；
- 同时报告 \(R^2\)、MAE、学习曲线 AUC 和达到目标 \(R^2\) 所需标签数；
- 不把一次运行或一个数据集的胜负写成普遍结论。

## R4：神经网络、GNN 与不确定性

推荐顺序：

1. **A05 GP-Net**：先回放公开 embedding 上的 GP＋entropy，不先重训旧 MEGNet；
2. **P04 PBNN**：比较普通 NN、部分贝叶斯 NN 与不确定性；
3. **A06 MOF RT-AL**：理解表征、代表性和大候选池；
4. **W03 MOF partial-charge GNN**：GNN＋MC Dropout；
5. **P05 DKL-on-STM**：DNN 表示＋GP＋真实仪器闭环。

统一完成标准：

- 明确不确定性来自 GP、后验权重、MC Dropout 还是模型集成；
- 检查不确定性与真实误差、覆盖率和校准的关系；
- 与 Random 使用相同预算、初始点和随机种子；
- 记录训练时间和硬件，不只报告预测指标。

## R5：相图、势函数与真实闭环

### A08 AIPHAD

先隐藏已有相标签，把完整数据作为离线 Oracle。比较 Least Confidence、Margin、Entropy 和 Random，并自行增加 macro-F1、边界误差或相图一致率。

### P09 DP-GEN / W04 ALEBREW / W05 FLARE

学习：

- MD 产生候选构型；
- 模型分歧或不确定性判断是否需要 DFT；
- 新构型标注后重训势函数；
- 为什么这属于学习更完整的势能面，而不是找最低能构型。

完整 DFT/HPC 闭环不是普通电脑的第一任务。优先回放公开数据、缩短 MD 或使用廉价计算器。

### W06 SARA / P07 CAMEO

先复现离线图表和决策逻辑，再讨论真实实验设备。软件可运行不等于机器人实验已复现。

## R6：粘合剂应用迁移

先复现至少两个公开材料 AL 数据集，再进入粘合剂：

```text
阶段 A：以全局误差和数据覆盖为目标
初始粘合剂数据 → AL 选下一批实验 → 化学组回填 → 重训

阶段 B：以性能极值为目标
固定或继续更新的代理模型 → BO 推荐高性能配方 → 实验验证
```

最低条件：

- 化学组确认输入字段、单位、测试标准、制备约束和安全规则；
- 保留失败实验、重复实验和批次信息；
- AL 阶段报告 MAE/RMSE/校准/标签效率；
- BO 阶段报告 best-so-far/regret/成功率；
- 两阶段分别设置 Random 或合理基线。

环氧案例可参考 Pruksawan et al.（2019），但不能把它的小数据设置直接当作所有粘合剂体系的通用定义。

## BO 副线

在主动学习 R1 跑通后，可独立学习：

1. P01 PV-Lab：GP/RF 与 BO 基准；
2. P02 NIST Fe-Co-Ni：不同采集函数与材料先验；
3. P03 Bgolearn：现代单/多目标工程框架；
4. P10 Augmented GP：物理概率模型增强 BO；
5. PS01 聚合物太阳能电池：NLP 数据、GP 采集和 contextual bandit；
6. H01 锂结晶 HITL：专家约束、分类边界和真实实验闭环；
7. L01 LLM-AL：最后评估外部 LLM/reranker 能否超过传统强基线。

副线主要报告 best-so-far、regret、top-k 和成功率，不能与 AL 的测试误差曲线混为一张结论。

## 最终统一比较

### 模型学习型 AL

| 表示/代理模型 | 不确定性/信息量 | 查询策略 |
|---|---|---|
| GP | GP posterior | Random / Max uncertainty / iGS |
| RF | 树间方差 | Random / Uncertainty / QBC |
| XGBoost ensemble | 模型间分歧 | Random / QBC / DAGS |
| PBNN | 后验方差 | Random / Uncertainty |
| GNN ensemble / MC Dropout | 模型间分歧 | Random / Uncertainty |
| DNN/GNN + GP | GP posterior | Random / Entropy / Uncertainty |

### 性质优化型 BO

| 代理模型 | 采集策略 |
|---|---|
| GP / RF / GNN | Random / Greedy / EI / UCB / TS |

所有方法必须使用相同数据、初始点、标签预算、batch size、测试协议和随机种子集合。任何算法结论至少跨两个公开材料数据集验证。
