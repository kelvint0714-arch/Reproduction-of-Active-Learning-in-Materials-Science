# P10｜增强高斯过程（物理先验 GP）BO/AL 复现

**路径状态**：`source-lock-needed`
**论文**：[Physics makes the difference: Bayesian optimization and active learning via augmented Gaussian process](https://doi.org/10.1088/2632-2153/ac4baa)
**正式论文卡**：[`papers/bayesian_optimization/physics_informed/P10_Augmented_GP.md`](../../../papers/bayesian_optimization/physics_informed/P10_Augmented_GP.md)

## 定位与边界

论文把带参数先验的物理模型放入 GP 均值，再让 GP 学残差：

```text
预测 = 参数化物理趋势 + GP 残差
```

它是可用于 BO/AL 的**结构化/增强 GP**，不是 PINN。最小复现使用作者 Forrester Notebook；忠实复现需对普通 GP、正确物理先验和错误先验做相同预算比较。普通电脑可运行 1D smoke，MCMC 重复会较慢；GPU 非必要。

## 来源锁定

一手来源：

- 论文 DOI：`10.1088/2632-2153/ac4baa`
- 论文原始代码：[ziatdinovmax/AugmentedGaussianProcess](https://github.com/ziatdinovmax/AugmentedGaussianProcess)，MIT
- 后续通用实现：[ziatdinovmax/gpax](https://github.com/ziatdinovmax/gpax)，MIT；只能用于 T3，不可替代 T2 原始 Notebook
- 原仓库无 tag；已核验入口为 `sGPBO_forrester.ipynb`。

```bash
git clone https://github.com/ziatdinovmax/AugmentedGaussianProcess.git \
  ../upstream/P10-augmented-gp
git -C ../upstream/P10-augmented-gp remote -v
git -C ../upstream/P10-augmented-gp branch --show-current
git -C ../upstream/P10-augmented-gp describe --tags --always --dirty
git -C ../upstream/P10-augmented-gp rev-parse HEAD
git -C ../upstream/P10-augmented-gp log -1 --format='%H %cI %s'
git -C ../upstream/P10-augmented-gp status --short
shasum -a 256 ../upstream/P10-augmented-gp/LICENSE \
  ../upstream/P10-augmented-gp/sGPBO_forrester.ipynb
```

如执行 gpax 扩展，另锁 release（不要用浮动 `main`）：

```bash
git clone --branch v0.1.9 --depth 1 \
  https://github.com/ziatdinovmax/gpax.git ../upstream/P10-gpax
git -C ../upstream/P10-gpax rev-parse HEAD
```

写入 `reproduction/runs/P10/source_lock.md`，分别标明“论文原实现”和“后续实现”。

## 环境

环境名：`repro-p10-augmented-gp`。原 Notebook 只在单元格中安装未固定的 `numpyro`，并导入 JAX 内部 API；没有作者环境锁。已核验 2022-03-18 的 commit 说明为 “Bump to jax>0.2.26”，但这不是完整版本约束。

```bash
conda create -n repro-p10-augmented-gp python=3.8 pip jupyter -y
conda activate repro-p10-augmented-gp
python -m pip install numpyro jax jaxlib numpy matplotlib
python -m pip check
python -m pip freeze > reproduction/runs/P10/pip-freeze-probe.txt
```

以上是兼容性探测，不是作者锁。若现代 JAX 因内部 API 变化失败，根据锁定 commit 日期逐步解析可运行组合；每次尝试写入 `environment_resolution.md`，成功后导出：

```bash
conda env export --no-builds > reproduction/runs/P10/environment.yml
```

不得在 T2 悄悄把 MCMC、核、先验或采集函数换成 gpax。任何 API patch 保存为独立 diff。

## T0｜来源、公式与 Notebook 核验

1. 固定原仓库 SHA、Notebook 哈希和许可证。
2. 导出 Notebook 代码，建立“论文公式—类/函数—单元格”映射。
3. 已核验 Notebook 包含普通 `ExactGP`、RBF/Matern、EI/UCB/uncertainty exploration/Thompson、2 个 seed points 和 12 个 exploration steps；最终值以锁定 SHA 为准。
4. 标出 Forrester、double-Lorentz/振荡案例，以及物理模型参数先验。
5. 记录 JAX/NumPyro 环境解析，不把当前 gpax 行为倒推为论文行为。

## T1｜最小 smoke test

复制 Notebook 到运行目录，将 MCMC 采样数和一个案例作为**仅 smoke 配置**缩小；保存 patch：

```bash
jupyter nbconvert --execute \
  --ExecutePreprocessor.timeout=3600 \
  --to notebook \
  --output-dir reproduction/runs/P10/raw_results \
  --output forrester_smoke.ipynb \
  ../upstream/P10-augmented-gp/sGPBO_forrester.ipynb
```

Smoke 成功要求：普通 GP 能拟合并输出有限均值/方差；至少一次 UCB 选点不重复；结构化均值参数有有限后验样本；固定 PRNGKey 可重复。

## T2｜忠实复现论文主结果

1. 恢复论文/Notebook 的 MCMC、seed points、12 步预算、噪声与 PRNGKey。
2. 在同一初始点和候选网格上分别运行普通 GP 与增强 GP。
3. 使用论文相同 UCB/EI 设置，保存每轮后验均值、方差、物理参数样本、采集分数和查询点。
4. 重画论文对应的预测区间、采集轨迹、外推与优化图。
5. 对照论文报告误差、regret/找到最优的步数和物理参数后验；若论文只给图，使用图像数字化值并注明误差。

T2 不使用 gpax 重写，不用真实函数全网格标签调先验。

## T3｜统一协议与错误先验消融

- 用 gpax `v0.1.9` 复刻相同任务，比较原实现与后续实现。
- 普通 GP、正确趋势、弱趋势、错误趋势、过强先验五组共享初始点和预算。
- 比较 prior predictive、posterior predictive、残差结构和物理参数可辨识性。
- 报告 simple regret、外推 MAE/RMSE、NLL、95% 区间覆盖率、校准和墙钟时间。
- 对 UCB 权重、观测噪声、MCMC 链数/样本数和核函数做消融。

## T4｜迁移到 DGEBA/粘合剂数据

只有具有可信、可写成参数函数的知识才进入均值函数，例如经实验验证的固化温度趋势或当量比附近的总体趋势；“认为 3/3 最好”不能作为物理定律。GP 学该趋势之外的残差，再由 EI/UCB 推荐候选。

先选定固定化学结构对并采集多个真实配比/固化条件点。与普通 GP 和错误先验并列，报告先验是否真的提高样本效率。当前 Synthetic 数据和跨结构平均曲面只可用于代码演练，不能验证物理先验。

## 公平性与评价

- BO：simple/normalized regret、best-so-far、达到阈值查询数、成功率。
- 代理：MAE/RMSE、NLL、区间覆盖率、校准误差和外推误差。
- 参数：真实/参考物理参数误差及后验区间；只在可辨识时解释。
- 所有方法共享初始点、候选网格、预算、PRNGKey 列表和观测噪声。
- Random、普通 GP+同采集函数是必需基线；错误先验是关键安全消融。
- 真实函数全网格只用于事后 regret，不用于先验/超参选择。

## 证据交付

```text
reproduction/runs/P10/
├── README.md
├── source_lock.md
├── environment.yml
├── environment_resolution.md
├── formula_code_map.md
├── configs/
├── patches/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

每次 MCMC 还要保存诊断（R-hat、ESS、divergence）、PRNGKey、样本文件和耗时。

## 停止条件

- Smoke 成功：一个 1D 案例完成 GP 拟合与至少一次合法选点，后验/方差有限且可重跑。
- 立即阻塞：无法解析 JAX 环境、MCMC 不收敛、Notebook patch 改变算法、物理公式/先验与论文无法对应。
- 只有原实现的主案例、普通 GP 对照、全部配置/轨迹、MCMC 诊断、论文图核对和偏差齐全后，状态才可改为 `completed`；gpax 重写本身不满足条件。
