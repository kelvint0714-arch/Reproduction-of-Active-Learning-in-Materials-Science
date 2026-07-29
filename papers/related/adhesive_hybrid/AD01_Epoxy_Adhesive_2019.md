# AD01｜小数据环氧粘合剂强度：作者所称 AL 与后续 BO

## 论文信息

- **正式题名**：*Prediction and optimization of epoxy adhesive strength from a small dataset through active learning*
- **作者**：Sirawit Pruksawan, Guillaume Lambard, Sadaki Samitsu, Keitaro Sodeyama, Masanobu Naito
- **年份 / 期刊**：2019，*Science and Technology of Advanced Materials* 20, 1010–1021
- **DOI**：[10.1080/14686996.2019.1673670](https://doi.org/10.1080/14686996.2019.1673670)
- **开放全文**：[PMC6818118](https://pmc.ncbi.nlm.nih.gov/articles/PMC6818118/)
- **NIMS 归档**：[Materials Data Repository](https://mdr.nims.go.jp/filesets/cb79e4f4-bdb7-4180-8ba8-b4c69d29cd60)

## 数据是什么

初始数据包含 32 个环氧粘合剂实验。每一行由四个可控变量和一个实测目标构成：

| 字段 | 含义 |
|---|---|
| \(MW_E\) | 双酚 A 型环氧树脂的分子量 |
| \(MW_C\) | 聚醚胺固化剂的分子量 |
| \(r\) | 胺基与环氧基的比例 |
| \(T_{cure}\) | 固化温度 |
| \(\sigma_{ad}\) | 单搭接剪切试验得到的接头强度，MPa |

论文把 4 个变量离散组合成 256 个候选实验条件。模型比较 Elastic Net、Random Forest 与 Gradient Boosting，并用交叉验证选择 Gradient Boosting。

## 两个阶段

### 阶段 1：作者称为 active learning

1. 用当前实测数据训练 Gradient Boosting；
2. 预测尚未实验的所有离散条件；
3. 按预测强度从高到低排序；
4. 每轮选择预测最高的 5 个条件做实验；
5. 将结果加入训练集并重训；
6. 共执行 3 轮，从 32 条增加到 47 条。

### 阶段 2：Bayesian optimization

作者把阶段 1 得到的数据交给后续 BO，并使用 Expected Improvement 继续寻找高强度条件。论文报告最终实验强度达到 \(35.8 \pm 1.1\) MPa。

## 严格分类

**本仓库分类：`related / author-labeled AL + BO`，不属于 `AL-core`。**

原因：

- 阶段 1 虽然“实验—回填—重训”形成闭环，作者也称其为 AL；
- 但选样规则是**预测强度最高的五个候选**，主要服务于高强度区域和后续优化；
- 它没有按最大不确定性、QBC、代表性或全局误差下降来选样；
- 阶段 2 明确是 EI 驱动的 BO。

因此按本仓库的严格定义，阶段 1 更接近 `greedy exploitation / 目标导向自适应取样`，阶段 2 是 `BO`。不能用这篇论文证明“最大不确定性主动学习”对粘合剂有效。

## 论文怎样评价

- 交叉验证 \(R^2\)、RMSE 和 MAE；
- 新增实验后的预测误差；
- 推荐候选的实测粘合强度；
- BO 最终得到的高强度条件。

论文报告 Gradient Boosting 的 \(R^2=0.85\)、RMSE 约 4.0 MPa、MAE 约 3.0 MPa。复现时还应增加：

- Random 选样基线；
- 真正的 uncertainty / diversity AL；
- 多随机种子；
- 固定测试集学习曲线；
- 与 Greedy、EI 的分阶段对照。

## 对当前课题的价值

可以直接借鉴：

- 小样本粘合剂数据的“配方/工艺输入 → 实测强度”基本形式；
- 实验候选池、每轮批量推荐和回填流程；
- 先改善数据覆盖/模型，再做目标优化的两阶段思想；
- 化学实验噪声应作为停止条件和评价参照。

不能直接照搬：

- 论文只覆盖特定的双酚 A 环氧树脂与聚醚胺体系；
- 四个离散变量不足以定义所有粘合剂；
- 预测最高值的 Greedy 策略不是严格的信息型 AL；
- 没有公开作者代码仓库可直接复现；
- 不能把论文的 32 条起始规模、候选网格和性能结论外推到未知粘合剂大类。

## 建议复现方式

1. 从公开正文/补充材料重建数据字典和离散候选池；
2. 先忠实重实现 Gradient Boosting＋Greedy top-5；
3. 增加 Random、最大不确定性和多样性基线；
4. 分别报告全局测试误差与 best-so-far；
5. 最后再加入 EI，明确画出“AL/数据获取阶段”和“BO/性能优化阶段”的边界。

这篇论文适合做粘合剂迁移案例，不适合作为第一次通用主动学习复现。
