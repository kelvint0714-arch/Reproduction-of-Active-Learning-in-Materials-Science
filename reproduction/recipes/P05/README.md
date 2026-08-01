# P05｜DKL-on-STM 复现路径

> 状态：`source-lock-needed`、`offline-only`。离线数据和模拟 oracle 可回放；真实
> STM/LabVIEW 闭环不在普通计算环境的复现范围内。

## 定位与边界

- 论文：*Uncovering multiscale structure-property correlations via active learning in scanning tunneling microscopy*，npj Computational Materials 11, 189 (2025)，DOI：<https://doi.org/10.1038/s41524-025-01642-1>。
- 分类：目标导向闭环主动学习（带 BO-like UCB）；DNN 将 30×30 STM patch 压到
  2 维表示，RBF-GP 给出均值/方差，UCB 选下一光谱测量位置。
- 最小复现：读取仓库内一份 `.hf5` 轨迹，核对 STM 图、光谱、DKL 坐标和 scalar
  元数据；再在公开 ground-truth 网格上执行少量模拟选点。
- 完整离线复现：按 Notebook 的 180×180 网格、30 像素窗口、10 像素步长、20 个
  初始随机点和逐点 UCB 回放，保存每轮坐标。
- 完整真实复现需要 STM、Nanonis 接口、LabVIEW 和实验样品，标记为 `offline-only`；
  模拟闭环成功不能写成仪器闭环成功。

## 来源锁定

- 正式论文和数据/代码声明：Nature DOI 页面。
- 作者仓库：<https://github.com/gnganesh99/DKL_on_STM>。
- 仓库无 tag；2026-07-31 核验 `main` 为
  `664963dbd4bdab5caa4997a2b4f5b9fa4385b902`。第一次正式运行前仍须再次解析并
  记录 SHA，因此状态含 `source-lock-needed`。
- 仓库包含 `Workflow_DKL_STM.ipynb`、`Analyze_DKL_data.ipynb`、五份 `.hf5`
  实验数据和 LabVIEW VI；模拟 Notebook 还从 Google Drive 下载 ground-truth 文件。
- 2026-07-31 未在仓库根目录看到许可证文件；在许可明确前，只克隆运行，不把代码或
  数据复制进本仓库。

```bash
git clone https://github.com/gnganesh99/DKL_on_STM.git \
  ../upstream/P05-dkl-on-stm
git -C ../upstream/P05-dkl-on-stm remote -v
git -C ../upstream/P05-dkl-on-stm branch --show-current
git -C ../upstream/P05-dkl-on-stm describe --tags --always --dirty
git -C ../upstream/P05-dkl-on-stm rev-parse HEAD
git -C ../upstream/P05-dkl-on-stm status --short
git -C ../upstream/P05-dkl-on-stm checkout \
  664963dbd4bdab5caa4997a2b4f5b9fa4385b902
```

```bash
find ../upstream/P05-dkl-on-stm/data -type f -name '*.hf5' -print0 |
  sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/P05/data_sha256.txt
```

Google Drive 文件 ID 和下载时间须从锁定 Notebook 原样抄入 `source_lock.md`；下载
后另算 SHA-256。Drive ID 不是内容哈希，不能单独作为数据锁。

## 环境

上游没有锁定环境文件。环境名建议 `al-p05-dkl-stm`，先从锁定 Notebook 的实际
import 构建最小环境，安装时保存解析版本；禁止猜测论文时的版本。

```bash
conda create -n al-p05-dkl-stm python=3.10 pip -y
conda activate al-p05-dkl-stm
python -m pip install jupyter nbconvert numpy pandas matplotlib scipy \
  scikit-learn h5py sidpy opencv-python gdown gpax atomai
python -m pip check
python -m pip freeze > reproduction/runs/P05/pip-freeze.txt
conda env export --no-builds > reproduction/runs/P05/environment.yml
python - <<'PY' > reproduction/runs/P05/hardware.txt
import platform, gpax
print(platform.platform())
print("gpax", getattr(gpax, "__version__", "unknown"))
PY
```

Notebook 内含 `!pip install` 和 `/content/...` 硬编码路径。忠实保留一份原 Notebook，
在 `reproduction/runs/P05/configs/` 维护参数化副本，并把每个路径修改写进
`deviations.md`；不能直接改上游文件后不留痕。

## T0｜来源和入口核验

```bash
conda activate al-p05-dkl-stm
python - <<'PY'
from pathlib import Path
import h5py
root = Path("../upstream/P05-dkl-on-stm/data")
for p in sorted(root.glob("*.hf5")):
    with h5py.File(p, "r") as h:
        print(p.name, list(h.keys()))
PY
python -c "import gpax, atomai, sidpy, cv2; print('imports ok')"
```

成功标准：五个 HDF5 文件可读且哈希已保存；Notebook 和
`next_DKL_coordinate.py`、`scalarizer.py` 均存在；不连接仪器。

## T1｜最小离线回放

1. 先执行参数化后的 `Analyze_DKL_data.ipynb`，只读仓库中的
   `Figure3_large_area_250nm.hf5`，验证四个光谱通道、STM 图像、`DKL Position`
   与 `DKL Scalar`。
2. 下载锁定 Notebook 指向的 ground-truth 文件，记录 URL/Drive ID、大小和
   SHA-256。
3. 将模拟 Notebook 设为固定 seed=3，保留其 30-pixel patch 和 coordinate
   step=10，只把 `exploration_steps` 临时缩为 2。
4. 执行并保存已执行 Notebook：

```bash
jupyter nbconvert --to notebook --execute \
  reproduction/runs/P05/configs/Workflow_DKL_STM_smoke.ipynb \
  --output-dir reproduction/runs/P05/raw_results \
  --output Workflow_DKL_STM_smoke.executed.ipynb \
  --ExecutePreprocessor.timeout=1800 \
  2>&1 | tee reproduction/runs/P05/logs/t1.log
```

成功标准：每轮重新训练 DKL、从未测点中选出一个 UCB 最大坐标、查询 ground-truth
scalar 并从候选池删除；输出至少含均值、方差、UCB 和选择坐标。缩短步数是 smoke
偏差，不得用于论文结论。

## T2｜忠实复现论文主结果

- 按论文设置从 20 个随机测量点开始；每轮重新初始化并训练 DKL，再逐点采集。
- 以锁定 Notebook 为准恢复完整训练步数、学习率、100 个模拟探索步和 beta 退火；
  保存每轮模型 seed、训练集索引、候选坐标、预测均值/方差、UCB 和真实 scalar。
- 分别复核大尺度区域、吸附物缺陷、替位缺陷、空位缺陷及多尺度 DKL 数据；实验
  HDF5 只能回放已记录轨迹，不能证明本机重新控制了 STM。
- 论文比较强调结构—性质图和目标区域发现；按图编号在 `comparison.md` 核对，而
  不是只汇报最终最大 scalar。
- 如果论文数据不足以重建某次在线模型状态，明确标为“轨迹回放”，不得插值伪造。

## T3｜统一协议重实现或消融

- 固定同一初始 20 点、预算和候选网格，比较 Random、原始像素上的普通 GP、DKL
  + 最大方差、DKL + UCB。
- 消融 patch 大小、步长、2 维 embedding、beta 调度；所有变化单独配置。
- 指标：候选池 MAE/RMSE、NLPD、95% coverage、累计最优 scalar、找到 top-k
  区域的查询数、坐标覆盖和墙钟时间。
- 图像相邻 patch 高度相关；划分测试区域时采用空间 block，而不是随机像素拆分，
  防止空间泄漏。
- scalarizer 的定义属于目标构造，必须固定；不得看完整 ground-truth 后再选择
  scalar 或 beta。

## T4｜迁移到粘合剂 / DGEBA

- 可迁移架构是“结构 embedding → GP → 不确定性/采集”，不是 STM 像素本身。
- 第一版以规范化表格描述符或固定分子 fingerprint 代替 DNN 图像 embedding，
  先与普通 GP、Random、DAGS 比较；样本很少时不要为了“用了神经网络”强上 DKL。
- 后续可尝试 `GNN embedding + GP`，但 embedding 预训练数据必须与测试结构隔离。
- AL 阶段目标为改善全空间预测时用最大方差；寻找高强度候选时才使用 UCB，并明确
  进入目标导向 AL/BO。
- 合成标签仅作离线 oracle；真实标签只能由化学组实验回填。

## 公平性与评价

- 固定候选网格、初始 20 点、总预算、batch size=1、seed 和 beta 调度。
- Random/GP/DKL 必须共享初始点和未测点；报告至少 5 个随机初始集的均值/标准差。
- 同时报全局误差、校准和目标发现指标，避免只用“发现了最大值”代替模型学习质量。
- 禁止在全图上预处理后随机拆 patch、用测量后的光谱构造输入、或用最终 scalar 图
  调采集参数。
- 仪器轨迹中的失败测量、漂移和坐标转换不得静默删除。

## 证据交付

```text
reproduction/runs/P05/
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

保存原/执行后 Notebook、每轮坐标 CSV、预测栅格、UCB 栅格、scalar、运行时间及
逐图核对。LabVIEW VI 和 HDF5 数据不复制进本仓库，除非许可明确允许。

## 停止条件

- T1 成功：数据可读，两轮闭环完成，两个新坐标互异且来自未测集合，输出无 NaN。
- 停止并标 `blocked`：无许可证导致计划中的再分发不合法、Drive 数据不可取得或
  无法锁定、GPax/AtomAI API 漂移使锁定 Notebook 无法执行且无可审计修复。
- 仪器不可用只限制真实闭环，离线工作保持 `offline-only`，不能标整体失败或完成。
- 只有固定来源/数据/环境、完整离线回放、所有日志结果、逐图核对和偏差说明齐全，
  才能把“离线复现”标 `completed`；真实 STM 复现必须另有仪器日志与安全审批。
