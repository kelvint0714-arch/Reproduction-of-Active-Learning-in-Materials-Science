# AD01｜小数据环氧胶黏剂 Greedy-AL＋BO 重实现路径

**路径状态**：`reimplementation-only`
**论文**：[Prediction and optimization of epoxy adhesive strength from a small dataset through active learning](https://doi.org/10.1080/14686996.2019.1673670)
**正式论文卡**：[`papers/related/adhesive_hybrid/AD01_Epoxy_Adhesive_2019.md`](../../../papers/related/adhesive_hybrid/AD01_Epoxy_Adhesive_2019.md)

## 定位与边界

论文先用 Gradient Boosting 预测 256 个离散条件，每轮选择预测最高 5 个进行 3 轮实验；后续再用 EI 做 BO。第一阶段是作者所称 AL，但采集规则是纯利用 Greedy，更准确地说是**目标导向自适应取样**；第二阶段是 BO。

- 最小重实现：用明确标为 synthetic/toy 的 4 变量数据验证 Gradient Boosting→top-5→回填→EI 流程。
- 忠实数值重实现：官方补充材料 Table S2 给出 32 个初始样本，正文 Table 2 给出 15 个新增实验；需双人转录并重建候选编码。
- 已核验未发现作者官方代码或 CSV/XLSX；NIMS MDR 公开正文 PDF，PMC 另公开补充 PDF，因此属于“有论文数据、无作者代码”的重实现。
- 湿实验完整复现需要环氧/固化剂、配制固化和单搭接剪切测试设备与安全审批。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1080/14686996.2019.1673670`
- 开放全文：[PMC6818118](https://pmc.ncbi.nlm.nih.gov/articles/PMC6818118/)
- NIMS MDR 数据集记录：[Prediction and optimization...](https://mdr.nims.go.jp/datasets/3531cb90-075f-4b92-9922-17ba4ba6d95e)
- MDR 当前文件为 `Prediction_and_optimization_of_epoxy_adhesive_strength_from_a_small_dataset_through_active_learning.pdf`，页面给出 MD5 `88e4d6266145472eba1ce8d298c9417e`；这不是 CSV/XLSX。
- PMC 官方补充材料：`TSTA_A_1673670_SM4906.pdf`（Table S2–S4 等）；Europe PMC XML 记录大小 428154 bytes、MD5 `477585c8bac5fe39d29bb8b3f458d3e1`。

```bash
mkdir -p ../upstream/AD01-epoxy-paper
curl -L \
  'https://mdr.nims.go.jp/filesets/cb79e4f4-bdb7-4180-8ba8-b4c69d29cd60/download' \
  -o ../upstream/AD01-epoxy-paper/article.pdf
curl -L \
  'https://pmc.ncbi.nlm.nih.gov/articles/instance/6818118/bin/TSTA_A_1673670_SM4906.pdf' \
  -o ../upstream/AD01-epoxy-paper/supplement.pdf
openssl dgst -md5 ../upstream/AD01-epoxy-paper/article.pdf \
  ../upstream/AD01-epoxy-paper/supplement.pdf
shasum -a 256 ../upstream/AD01-epoxy-paper/article.pdf \
  ../upstream/AD01-epoxy-paper/supplement.pdf
```

若 URL 变化，从 PMC/MDR 页面人工下载并记录最终 URL、日期、许可、文件名、大小、MD5/SHA-256。PDF 不提交本仓库。将“无官方代码/结构化表、但有可转录补充表”的检索结果和日期写入 `reproduction/runs/AD01/source_lock.md`。

## 环境

环境名：`repro-ad01-epoxy`。因为没有作者环境，下面只定义本项目重实现环境，不能称为原环境：

```bash
conda create -n repro-ad01-epoxy python=3.11 pip -y
conda activate repro-ad01-epoxy
python -m pip install numpy pandas scikit-learn scipy matplotlib openpyxl
python -m pip check
python -m pip freeze > reproduction/runs/AD01/pip-freeze.txt
conda env export --no-builds > reproduction/runs/AD01/environment.yml
```

锁定 sklearn 的 `GradientBoostingRegressor`、交叉验证与自编 EI 实现版本。若将论文 PDF 表格手工转录，双人复核并保存 `transcription_audit.md`。

## T0｜论文、数据可得性与算法核验

1. 按正文/补充材料逐项提取变量：环氧分子量 \(MW_E\)、聚醚胺分子量 \(MW_C\)、胺/环氧比 \(r\)、固化温度 \(T_{cure}\)、剪切强度 MPa。
2. 核对 32 个初始样本、256 候选、3×5 新实验、最终 47 样本及 BO 阶段的真实顺序。
3. 将论文超参数、CV 方案、Greedy top-5 和 EI 公式写入 `paper_protocol.md`；未知项标 `NR`，不猜。
4. 从补充材料 Table S2 双人独立转录初始 32 条，从正文 Table 2 转录三轮 15 条；逐格对比并保留页码/校验。
5. 确认 MDR 文件性质和权利，不把 PDF 误称数据集。

## T1｜最小 smoke test

创建不含任何论文伪造数值的 toy 4D 网格和带噪声目标：

1. 随机/空间覆盖选择 32 条；
2. 拟合 Gradient Boosting；
3. 从未标注池选择预测最高 5 条；
4. 揭示 toy Oracle 并回填三轮；
5. 在同一 47 条上运行 GP-EI。

Smoke 成功只证明实现可运行：候选不重复、每轮模型只看已揭示标签、32→37→42→47 计数正确、Greedy 与 EI 分阶段。所有图标注 `TOY / NOT PAPER DATA`。

## T2｜忠实复现论文主结果

本阶段按“论文数据重实现”执行，不称作者代码复现：

1. 固定正文/补充 PDF 哈希和转录审计，重建 256 候选。
2. 按论文模型比较 Elastic Net、RF、Gradient Boosting，使用原 CV/超参选择。
3. 依次回放三轮 Greedy top-5，不能用后续 15 条提前调模型。
4. 用阶段 1 完成后的数据初始化论文 EI BO，保存每轮均值、方差、EI 和实测强度。
5. 核对报告的 Gradient Boosting \(R^2=0.85\)、RMSE≈4.0 MPa、MAE≈3.0 MPa 以及最终 \(35.8\pm1.1\) MPa；这些数字是核对目标，不是容许硬编码的答案。

若 Table S2/正文表无法完整恢复逐行值，T2 才保持“不可执行”，不要用合成数据填空。

## T3｜统一协议与消融

- 为 Greedy 增加 Random、最大不确定性、QBC/多样性与 GP-EI 基线。
- 固定独立测试集或 nested CV，分别报告全局预测质量和最优发现效率。
- 以配对种子比较 batch=1/5、三个模型、Greedy/EI/不确定性。
- 检查离散变量 one-hot/连续编码、候选重复和小样本超参过拟合。
- 用实验重复的标准差定义“改进是否超过噪声”停止规则。

## T4｜迁移到当前 DGEBA/离子液体/多酚课题

借鉴“配方/工艺→实测强度”的表结构和 Greedy→BO 两阶段，不照搬 32、256、5 或论文最优条件。当前课题先由化学组明确胶黏剂大类、添加量单位、固化和测试标准。

离线 Synthetic 表可测试流程，但输入要排除标签派生模拟量。真实阶段先用 Random/代表性策略增加覆盖，再用 EI 优化；固定结构对并有多个真实比例点前，不进行小数配比 BO。每个推荐都需化学组审核可制备性。

## 公平性与评价

- 监督预测：nested/固定方案的 \(R^2\)、MAE、RMSE 与重复间方差。
- 目标优化：best-so-far、simple regret、达到强度阈值的实验数、成功率和累计成本。
- Random、Greedy 和 EI 必须分开；不能把 Greedy 成功归因于不确定性 AL。
- 三轮新增实验按时间回放，后续标签不得进入早期预处理/CV。
- 相同树脂/固化剂家族分组检查结构泄漏；实验重复不可拆到两侧。
- 候选池之外的 BO 推荐要单独标注连续外推风险。

## 证据交付

```text
reproduction/runs/AD01/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── paper_protocol.md
├── transcription_audit.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

论文 PDF 留在外部 `../upstream/`；若作者提供数据，保存原件只读副本、许可和哈希。

## 停止条件

- Smoke 成功：toy 数据完成 3 轮 Greedy 和后续 EI，严格无标签泄漏，且所有输出明确标 synthetic。
- 立即阻塞忠实重实现：补充表无法可靠转录、变量单位或候选编码不明、只能从低清图猜数、实验条件无法安全执行。
- 只有经审计的逐行转录、论文协议、47 条时间顺序、BO 轨迹、指标核对和偏差齐全后才可 `completed`；仍须注明“无作者代码、论文数据重实现”。
