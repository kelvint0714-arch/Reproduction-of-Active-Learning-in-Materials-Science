# P04｜PBNN / NeuroBayes 复现路径

> 状态：`recipe-ready`。本文件给出可执行路径，不表示论文结果已经在本机复现。

## 定位与边界

- 论文：*Active and transfer learning with partially Bayesian neural networks for materials and chemicals*，Digital Discovery (2025)，DOI：<https://doi.org/10.1039/D5DD00027K>。
- 正确分类：以降低候选池整体预测误差为目标的主动学习；采集信号是 PBNN 后验预测方差，不是寻找最大值的 BO。
- 核心比较：确定性 NN、GP、DKL、完全贝叶斯 NN（FBNN）和部分贝叶斯 NN（PBNN）；另有“理论/模拟预训练权重作为贝叶斯先验”的迁移学习实验。
- 最小复现：用作者随 `paper_zenodo` 版本发布的 ESOL 特征，运行 1 个种子、少量轮次的 PBNN 池式主动学习，确认“训练→方差选点→回填→重训→记录指标”闭环。
- 完整复现：按论文脚本原参数运行 ESOL、FreeSolv、NIMS Steel、HTEM 和带隙迁移设置，并逐图核对。
- 门槛：T0/T1 可在普通 CPU 或 Apple Silicon 上尝试；NUTS 后验采样很慢，忠实的多种子、多数据集实验建议 GPU/长时任务。无需仪器、DFT 或外部 API。

## 来源锁定

- 正式论文与补充材料：RSC DOI 页面。
- 作者代码：<https://github.com/ziatdinovmax/NeuroBayes>。
- 论文专用 tag：`paper_zenodo`；2026-07-31 核验其 commit 为 `c56327998052ed05499c79a731bd108733a678c8`。
- ESOL 等论文脚本和部分数据位于 `active_learning_scripts/`；不要用不断变化的 `main` 代替论文 tag。
- `setup.py` 声明 MIT；首次执行仍须保存仓库中的实际许可文本/元数据。各外部数据集的许可须分别核对，不能由代码许可推导。

```bash
git clone --branch paper_zenodo --single-branch \
  https://github.com/ziatdinovmax/NeuroBayes.git \
  ../upstream/P04-neurobayes
git -C ../upstream/P04-neurobayes remote -v
git -C ../upstream/P04-neurobayes branch --show-current
git -C ../upstream/P04-neurobayes describe --tags --always --dirty
git -C ../upstream/P04-neurobayes rev-parse HEAD
git -C ../upstream/P04-neurobayes status --short
test "$(git -C ../upstream/P04-neurobayes rev-parse HEAD)" = \
  "c56327998052ed05499c79a731bd108733a678c8"
```

把命令输出、访问日期、`requirements.txt`、`setup.py`、许可信息写入
`reproduction/runs/P04/source_lock.md`。对实际使用的数据文件执行：

```bash
find ../upstream/P04-neurobayes/active_learning_scripts \
  -type f \( -name '*.csv' -o -name '*.npz' \) -print0 |
  sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/P04/data_sha256.txt
```

## 环境

环境名建议为 `al-p04-neurobayes-paper`。优先依据论文 tag 自带
`requirements.txt` 和 `setup.py` 建环境；其中声明 Python `>=3.9`、JAX/JAXLIB
`<=0.4.31`，但没有完整锁文件，禁止再凭猜测固定其他依赖版本。

```bash
conda create -n al-p04-neurobayes-paper python=3.10 pip -y
conda activate al-p04-neurobayes-paper
python -m pip install --upgrade pip
python -m pip install -r ../upstream/P04-neurobayes/requirements.txt
python -m pip install scikit-learn pandas torch gpytorch
python -m pip install -e ../upstream/P04-neurobayes
python -m pip check
python -m pip freeze > reproduction/runs/P04/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P04/environment.yml
python - <<'PY' > reproduction/runs/P04/hardware.txt
import platform
import jax
print(platform.platform())
print("jax", jax.__version__)
print(jax.devices())
PY
```

若 JAX 后端安装失败，只能按 JAX 官方对应平台说明调整，并把命令和原因写入
`deviations.md`；不得悄悄换到当前 NeuroBayes API。

## T0｜来源和入口核验

```bash
conda activate al-p04-neurobayes-paper
python -c "import neurobayes, jax; print(neurobayes.__file__); print(jax.devices())"
python ../upstream/P04-neurobayes/active_learning_scripts/esol/pbnn.py --help
python ../upstream/P04-neurobayes/active_learning_scripts/esol/gp.py --help
```

成功标准：commit 精确匹配；`esol.npz` 能读出 `features` 与 `targets`，且样本数
一致；两个命令入口能显示参数。将形状、dtype、缺失值数量和哈希写进日志。

## T1｜最小离线回放

在脚本所在目录运行，避免其相对路径导入失效：

```bash
cd ../upstream/P04-neurobayes/active_learning_scripts/esol
python pbnn.py \
  --seeds 1 \
  --exploration_steps 2 \
  --sgd_epochs 20 \
  --probabilistic-layer-names Dense2 Dense4 \
  --hidden-dims 8 8 8 8 \
  --input-file esol.npz \
  --output-dir "$OLDPWD/reproduction/runs/P04/raw_results/smoke_pbnn" \
  2>&1 | tee "$OLDPWD/reproduction/runs/P04/logs/t1_pbnn.log"
```

这里缩短轮次/epoch 只用于 smoke test，必须在 `deviations.md` 标明，不能与论文数值
比较。检查输出 pickle/JSON 中每轮都有 `mse`、`mae`、`nlpd`、`coverage`，且已标记
样本每轮恰好增加 1。

## T2｜忠实复现论文主结果

1. 从锁定 tag 读取每个数据集脚本的默认参数，不手工“优化”参数。
2. ESOL 至少运行 `detnn.py`、`gp.py`、`dkl.py`、`bnn.py`、`pbnn.py`；使用脚本默认
   5 个种子、5% 初始标记池、200 次逐点采集，以及各脚本自己的训练/采样参数。
3. 对 FreeSolv、NIMS Steel、HTEM 使用同一原则，保存每轮候选池预测、选择索引、
   后验均值/方差、墙钟时间和峰值内存。
4. 迁移实验必须把预训练来源数据、目标实验数据、权重到先验的映射和从零训练对照
   分开记录；不得让目标测试标签进入预训练或特征标准化。
5. 从作者结果文件读取论文曲线作为“参考”，但重跑结果另存，不覆盖作者文件。
6. 在 `comparison.md` 按论文图/表逐项比较均值、种子离散度和计算成本；差异不应只
   报一个最终数字。

## T3｜统一协议重实现或消融

- 固定同一候选池、初始索引、采集预算和种子，比较 Random、GP 最大方差、DKL、
  FBNN、PBNN；确定性 NN 若没有可用不确定性只能作为预测基线，不能伪装成方差采集。
- 消融概率层数量、后验样本数、是否使用预训练先验，并报告性能—成本曲线。
- 同时报告误差与不确定性质量：MAE/RMSE、NLPD、95% 区间覆盖率、区间宽度、
  不确定性—绝对误差相关性和墙钟时间。
- 标准化器每一轮只在当前已标记集上拟合；保留固定、从不参与采集的测试集。
- 作者脚本在整个特征矩阵上先拟合 `StandardScaler` 的行为必须作为潜在信息泄漏
  单独记录；忠实回放与“无泄漏修正版”要分成两组结果。

## T4｜迁移到粘合剂 / DGEBA

1. 只使用实验前可知的离子液体、多酚结构描述符、添加量和工艺条件；删除
   `Crosslink_density`、预测 Tg/模量、相容性、相分离风险和网络韧性等可能参与
   合成标签生成的字段。
2. 第一阶段只把现有 `Synthetic` 标签当离线 oracle，验证选样代码，结论必须标
   “算法回放”，不能声称发现真实胶黏剂。
3. 固定一个按结构组留出的测试集；初始集、候选池和测试集按
   `IL_ID + Polyphenol_ID` 分组，避免同结构泄漏。
4. 比较 Random、GP、DAGS 和 PBNN 的 MAE—标记预算曲线及不确定性校准；PBNN
   只有在多种子下稳定优于 Random 才进入真实实验候选。
5. 真实实验阶段由化学组逐轮回填标签；固定结构后的小数配比优化是后续独立 BO，
   不与本任务混为一谈。

## 公平性与评价

- 固定并保存候选 ID、初始 5% 索引、独立测试索引、总预算、batch size=1、种子
  `1–5`；所有方法使用同一份索引。
- 主指标：测试 MAE/RMSE 随已标记样本数的曲线及 AULC；辅助指标：NLPD、95%
  coverage、平均区间宽度、运行时间。
- Random 至少按同样种子重复；报告均值和标准差，不能只挑最好 seed。
- 不得用全数据标准化、测试集调参、采集后重划测试集或挑选作者保存结果中的最佳轮次。
- 分子数据按论文忠实划分回放后，再增加 scaffold/结构留出压力测试；两者分开报告。

## 证据交付

执行前建立：

```text
reproduction/runs/P04/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── data_sha256.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

必须保存：每轮选择索引、每轮预测与方差、所有 seed 的原始指标、聚合脚本和图表，
以及论文图表的逐项核对。上游仓库、论文 PDF 和未确认再分发许可的数据不提交。

## 停止条件

- T1 成功：固定来源可安装；两轮闭环结束；输出可解析；已标记集每轮只增加一个点。
- 立即停止并标 `blocked`：tag/commit 不匹配、数据哈希变化、NUTS 持续发散/产生
  非有限方差、脚本实际使用了测试标签或依赖无法在锁定 API 下安装。
- T2 结果与论文偏离时先记录偏差，不能调参直到“看起来一致”。
- 只有来源、环境、数据、全部命令/日志、原始和处理结果、论文逐图核对、失败与修改
  说明齐全，才可把状态改为 `completed`。
