# W06｜SARA 分层主动学习复现路径

> 状态：`recipe-ready`、`offline-only`。公开原始数据上的内/外层 AL benchmark
> 可回放；真实激光合成、成像和光谱机器人闭环不在本 recipe 的本地范围内。

## 定位与边界

- 论文：*Autonomous materials synthesis via hierarchical active learning of
  nonequilibrium phase diagrams*，Science Advances 7, eabg4930 (2021)，
  DOI：<https://doi.org/10.1126/sciadv.abg4930>。
- 分类：分层主动学习。内层选择同一条温度—时间 stripe 上的表征点，外层选择下一
  合成 stripe；同时学习非平衡相图/梯度。
- 最小复现：实例化两个 Julia 项目并跑测试；读取准备好的 JSON/HDF5 后分别执行
  内层和外层 acquisition benchmark 的缩短版。
- 忠实离线复现：从 Cornell eCommons 原始图像/光谱开始预处理，运行论文
  Fig. 2–4 的 benchmark 与绘图脚本。
- 完整真实复现需要激光尖峰退火平台、自动成像/反射光谱及实验控制，标
  `offline-only`，不可用数据回放冒充机器人实验。

## 来源锁定

- 正式论文：AAAS DOI 页面。
- 官方代码：<https://github.com/gomes-lab/SARA_ScienceAdvances>，MIT。
- 2026-07-31 核验 `master` commit：
  `61848d1c92a66bd58c8c195e5b2bb250ef8efb51`。
- 原始数据：Cornell eCommons，DOI <https://doi.org/10.7298/h63q-9r54>。
- 代码自带 `GaussianDistributions.jl/Manifest.toml` 与
  `SARA.jl/Manifest.toml`；它们是首选环境锁。
- eCommons 数据许可必须从归档元数据单独记录；不能由代码 MIT 许可推导。

```bash
git clone https://github.com/gomes-lab/SARA_ScienceAdvances.git \
  ../upstream/W06-sara
git -C ../upstream/W06-sara remote -v
git -C ../upstream/W06-sara branch --show-current
git -C ../upstream/W06-sara describe --tags --always --dirty
git -C ../upstream/W06-sara rev-parse HEAD
git -C ../upstream/W06-sara status --short
git -C ../upstream/W06-sara checkout \
  61848d1c92a66bd58c8c195e5b2bb250ef8efb51
```

从 DOI 页面下载原始数据后：

```bash
find reproduction/runs/W06/raw_results/ecommons -type f -print0 |
  sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/W06/data_sha256.txt
```

保存 DOI 元数据、文件 URL/名称/大小/checksum、访问日期和许可到 `source_lock.md`。

## 环境

Julia 环境以仓库 Manifest 为准；上游说明 Julia `>1.6.2`，记录实际 Julia 版本，
不要猜测论文版本。Python 预处理环境名建议 `al-w06-sara-preprocess`，只按实际
import 安装并导出解析版本。

```bash
julia --version | tee reproduction/runs/W06/julia_version.txt
julia --project=../upstream/W06-sara/GaussianDistributions.jl \
  -e 'using Pkg; Pkg.instantiate(); Pkg.status()'
julia --project=../upstream/W06-sara/SARA.jl \
  -e 'using Pkg; Pkg.develop(path="../upstream/W06-sara/GaussianDistributions.jl"); Pkg.instantiate(); Pkg.status()'
cp ../upstream/W06-sara/SARA.jl/Project.toml \
  reproduction/runs/W06/Project.toml
cp ../upstream/W06-sara/SARA.jl/Manifest.toml \
  reproduction/runs/W06/Manifest.toml
```

```bash
conda create -n al-w06-sara-preprocess python=3.10 pip -y
conda activate al-w06-sara-preprocess
python -m pip install numpy scipy matplotlib h5py
python -m pip freeze > reproduction/runs/W06/pip-freeze.txt
conda env export --no-builds > reproduction/runs/W06/environment.yml
```

若预处理脚本导入额外包，以错误/源码为证据补装并记录，不凭猜测预钉版本。

## T0｜来源和入口核验

```bash
julia --project=../upstream/W06-sara/GaussianDistributions.jl \
  -e 'using Pkg; Pkg.test()' \
  2>&1 | tee reproduction/runs/W06/logs/t0_gaussian_tests.log
julia --project=../upstream/W06-sara/SARA.jl \
  -e 'using Pkg; Pkg.test()' \
  2>&1 | tee reproduction/runs/W06/logs/t0_sara_tests.log
```

核验 `ProcessingData/get_gp-bias.py`、`get_legcoeff.py`、inner/outer benchmark 和
plot 脚本存在。检查脚本中的相对路径，所有路径修改放到 `configs/` 副本。

## T1｜最小离线回放

1. 若已下载原始数据，先按 README 放到独立工作目录，运行：

```bash
conda activate al-w06-sara-preprocess
python reproduction/runs/W06/configs/get_gp-bias_smoke.py \
  2>&1 | tee reproduction/runs/W06/logs/t1_bias.log
python reproduction/runs/W06/configs/get_legcoeff_smoke.py \
  2>&1 | tee reproduction/runs/W06/logs/t1_legendre.log
```

2. 用 `inner_data_organizer.jl` 生成内层 JSON；在配置副本中将采样数/stripe 数缩小，
   分别运行 inner/outer acquisition benchmark：

```bash
julia --project=../upstream/W06-sara/SARA.jl \
  reproduction/runs/W06/configs/inner_acquisition_benchmark_smoke.jl \
  2>&1 | tee reproduction/runs/W06/logs/t1_inner.log
julia --project=../upstream/W06-sara/SARA.jl \
  reproduction/runs/W06/configs/outer_acquisition_benchmark_smoke.jl \
  2>&1 | tee reproduction/runs/W06/logs/t1_outer.log
```

成功标准：inner/outer 都至少执行 2 次查询，输出 HDF5 含 `rmse`、`r2` 和 policy
names，选择点不重复。所有缩短参数和路径 diff 写入 `deviations.md`。

## T2｜忠实复现论文主结果

- 从原始图像/光谱开始运行官方预处理，固定生成的 `bias.json` 和
  `legendre_coefficients.json` 哈希。
- 按 README 顺序运行 inner kernel/acquisition benchmark 与 plot，复现 Fig. 2；
  运行 outer kernel/acquisition、gradient map/learning/plot，复现 Fig. 3–4。
- 使用脚本原始 `nsample=128`、`nstripes=48`、kernel length scales、UCB alpha、
  noise correction 和 Random 重复设置；任何 bug 修复另列 T3。
- 保存每个 policy 的查询序列、RMSE/R²、梯度 R²、噪声估计、随机重复与线程数。
- 官方脚本的相对路径曾指向 `SARA/NatCom2020` 等历史目录；路径修正须逐项记录，
  不能静默把预生成结果当新计算结果。
- 真实合成只回放已记录数据；没有机器人仪器日志时不可声称重新合成 Bi₂O₃。

## T3｜统一协议重实现或消融

- 同一初始状态、预算和 seed 比较 Random、uncertainty、integrated uncertainty、
  integrated gradient uncertainty、UCB、stripe UCB。
- 分别消融专用 iSARA/oSARA kernel、RGB bias、input-noise correction 和 hierarchical
  stripe acquisition。
- 指标：property/gradient RMSE 与 R²、到 R² 阈值的查询数、stripe 覆盖、墙钟时间。
- 锁定源码的 `inner_acquisition_benchmark.jl` 中梯度 RMSE 行使用了 `δ` 而非
  `∂δ`；T2 忠实保留并标注，T3 可修复后另跑，不能覆盖原结果。
- Random 至少 20 次（资源允许时 32 次），其他策略使用相同初始条件。

## T4｜迁移到粘合剂 / DGEBA

- 分层结构非常适合未来实验：内层可在一个固定结构配方上选择最有信息的固化/测试
  条件，外层选择下一离子液体—多酚—添加量配方。
- 前提是明确两层 oracle、成本和可复用关系；当前合成表不能代替真实内层实验。
- 候选约束（可制造、相容、总添加量、安全）须在采集前定义。
- 比较普通单层 AL 与分层 AL 的真实实验次数、预测误差和失败率；若没有成本优势，
  不因形式复杂继续使用。

## 公平性与评价

- 固定初始点/stripe、总点数和 stripe 预算、seed、noise model 和测试网格。
- 所有策略共享同一离线 oracle；Random 使用足够重复并报告标准误。
- 图像、相邻温度点和同一 stripe 高相关，训练/测试按 stripe 或实验批次分组。
- 完整相图与梯度只能用于评估，不能提前用于采集或 kernel 调参。
- inner 和 outer 指标分别报告，并给出合并的实验成本。

## 证据交付

```text
reproduction/runs/W06/
├── README.md
├── source_lock.md
├── environment.yml
├── Manifest.toml
├── Project.toml
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

保存预处理产物哈希、每个 query、各 policy 原始 HDF5、线程/RNG、图表和逐图核对。
原始实验数据是否提交取决于 eCommons 许可。

## 停止条件

- T1 成功：两个 Julia 包测试通过，inner/outer 缩短闭环均产生可解析 HDF5。
- 停止并标 `blocked`：Manifest 无法解析且无可审计兼容方案、原始数据缺失/哈希
  变化、路径修复无法对应官方输入或输出含非有限值。
- 无机器人/激光平台时保持 `offline-only`，离线复现仍可完成。
- 只有固定来源/环境/数据、全预处理、完整 benchmark、随机基线/消融、逐图核对和
  偏差说明齐全，才可标“离线 `completed`”；真实闭环需另附仪器证据。
