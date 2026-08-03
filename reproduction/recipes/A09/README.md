# A09｜ANI-1x / QBC 化学空间主动学习复现路径

> 状态：`source-lock-needed`、`offline-only`。公开模型与 COMP6 可回放；论文完整
> QBC 数据生成链没有核验到固定的一键入口。

## 定位与边界

- 论文：*Less is more: Sampling chemical space with active learning*，
  *The Journal of Chemical Physics* 148, 241733 (2018)，DOI：
  <https://doi.org/10.1063/1.5023802>。
- 分类：分子势能面/化学空间的 QBC 主动学习。committee 分歧选择新量化标签，目标
  是降低独立 COMP6 上的能量和力误差，不是寻找极值的 BO。
- 最小复现：用现代官方 TorchANI 读取 ANI-1x 预训练模型，在 COMP6 小子集上核对
  能量/力误差管线。
- 忠实复现：恢复论文的候选生成、committee 训练、分歧阈值、量化标签与多轮重训。
- 当前公开产物足以评估最终模型，但没有核验到论文全部 AL 轮次的固定代码 release，
  因此不能把 T1 写成论文 AL 闭环已复现。

## 来源锁定

- 正式论文 DOI 与开放预印本 arXiv:1801.09319。
- 论文时代接口：<https://github.com/isayev/ASE_ANI>，MIT；2026-08-03 核验
  `master` 为 `2a4069222ca9b2ef2a41231d01f1a7011b529994`。上游已弃用，要求
  Python 3.6、CUDA 9.2 和 Linux/NVIDIA。
- COMP6：<https://github.com/isayev/COMP6>，MIT；固定 commit
  `79f41c156f8e19506fe951b5513b98e7c534a503`。
- ANI-1x 读取工具：<https://github.com/aiqm/ANI1x_datasets>，MIT；固定 commit
  `c6b6d20b9915a4534204800b634fc1f8ee0a08bc`。
- 现代官方实现：<https://github.com/aiqm/torchani>，MIT；当前 smoke commit
  `ed1f202992d3a6d4456ce1b8c3697fed5bc5b097`。它不是 2018 论文环境。
- ANI-1x 数据：Figshare v1，DOI
  <https://doi.org/10.6084/m9.figshare.10047041.v1>，CC0；
  `ani1x-release.h5` 为 5,590,846,027 bytes，MD5
  `98090dd6679106da861f52bed825ffb7`。

```bash
git clone https://github.com/isayev/COMP6.git ../upstream/A09-COMP6
git -C ../upstream/A09-COMP6 checkout \
  79f41c156f8e19506fe951b5513b98e7c534a503
git clone https://github.com/aiqm/ANI1x_datasets.git \
  ../upstream/A09-ANI1x-datasets
git -C ../upstream/A09-ANI1x-datasets checkout \
  c6b6d20b9915a4534204800b634fc1f8ee0a08bc
git clone https://github.com/aiqm/torchani.git ../upstream/A09-torchani
git -C ../upstream/A09-torchani checkout \
  ed1f202992d3a6d4456ce1b8c3697fed5bc5b097
```

在 `reproduction/runs/A09/source_lock.md` 记录三个 commit、论文/数据 DOI、
Figshare 元数据 JSON、文件大小、MD5、本地 SHA-256 与各自许可证。只有准备 T2 时才
克隆旧 `ASE_ANI`；不要为 T1 下载 5.59 GB 全量数据。

## 环境

T1 建议新建 CPU 环境 `al-a09-ani-smoke`。2026-08-03 核验 TorchANI README 在
安装问题修复前建议固定 `2.2.4`；执行时仍需再次核对官方说明。

```bash
conda create -n al-a09-ani-smoke python=3.11 pip -y
conda activate al-a09-ani-smoke
python -m pip install 'torchani==2.2.4' 'h5py>=3.10,<4' numpy
python -m pip check
python -c "import torch, torchani; print(torch.__version__, torchani.__version__)"
python -m pip freeze > reproduction/runs/A09/pip-freeze.txt
conda env export --no-builds > reproduction/runs/A09/environment.yml
```

不要在当前 macOS 环境强装旧 ASE_ANI 的 CUDA 9.2 二进制。T2 必须另建隔离的历史
Linux/CUDA 容器，并保存容器 digest；现代 TorchANI 结果和历史 NeuroChem 结果分开。

## T0｜来源和入口核验

```bash
git -C ../upstream/A09-COMP6 status --short
git -C ../upstream/A09-ANI1x-datasets status --short
git -C ../upstream/A09-torchani status --short
test -f ../upstream/A09-COMP6/LICENSE
test -f ../upstream/A09-ANI1x-datasets/LICENSE
test -f ../upstream/A09-torchani/LICENSE
find ../upstream/A09-COMP6/COMP6v1 -name '*.h5' | sort \
  > reproduction/runs/A09/comp6_files.txt
```

核对 COMP6 README 的误差单位是 kcal/mol 与 kcal/mol/Å，且“总能量、相对能量、力”
均同时报告 MAE/RMSE。保存各子集分子/构型数，不从论文图中猜分割。

## T1｜最小离线回放

1. 只选 COMP6 的一个小子集与固定前若干构型，保存构型 ID 清单；
2. 用官方 TorchANI ANI-1x 预训练 ensemble 在 CPU/MPS 上计算能量和力；
3. 使用 COMP6 定义重算总能量、相对能量和力的 MAE/RMSE；
4. 保存逐构型预测与聚合脚本、单位转换、异常构型和运行时间；
5. 与 COMP6 README 的全量参考值只做量级检查，不能用小子集要求逐数相等。

成功标准：固定子集可重复读取；预测与误差均为有限值；同一 seed/构型清单重复运行
结果一致。T1 名称必须是“现代实现的预训练模型评估 smoke”。

## T2｜忠实复现论文主结果

1. 从论文和补充材料解析全部候选生成器、初始训练集、committee 大小、分歧定义与
   查询阈值；找不到的参数明确写 `unverified`，不得用现代默认值补齐。
2. 锁定论文时代 ANI/NeuroChem、量化计算程序、泛函/基组和每轮数据版本。
3. 按原流程生成候选、在标签揭示前计算 committee 分歧、查询量化能量/力并重训。
4. 保存每轮候选数、查询数、失败量化计算、训练集哈希、模型 seed 与 COMP6 结果。
5. 复现“10% 数据达到 ANI-1、25% 数据优于 ANI-1”的学习曲线和论文表格；若原始
   每轮数据/代码不可取得，T2 保持 `blocked`，不以最终 ANI-1x 模型代替。

## T3｜统一协议重实现或消融

- 在同一初始集、候选池、量化标签预算和独立测试集下比较 Random 与 QBC。
- 消融 committee 大小、分歧阈值、批量大小、采样器和每轮重训方式。
- 指标：总能量/相对能量/力 MAE 与 RMSE、最坏误差、校准、覆盖、查询数和总成本。
- 按分子骨架/来源分组拆分训练与测试，避免同一分子的相近构象跨集合泄漏。
- 现代模型或缩小候选池必须写入 `deviations.md`，不能声称忠实复现。

## T4｜迁移到粘合剂 / DGEBA

- 可迁移思想是“多个模型分歧 → 只查询高价值的新标签”；表格任务可用 RF/XGBoost/
  NN committee 选择下一配方，不需要 ANI 或量化化学环境。
- 若研究 DGEBA 固化、界面或反应势能面，必须先定义原子结构、元素范围、标签方法与
  宏观性能之间的跨尺度关系；现有配方 Excel 不能直接输入 ANI-1x。
- 迁移实验仍需 Random、固定测试集、相同标签预算和按配方族分组的防泄漏拆分。

## 公平性与评价

- 所有策略固定初始训练集、候选池、committee seed、批量与总量化标签预算。
- 查询分歧必须在新标签揭示前计算；测试集只用于评估。
- 同分子相邻构象高度相关，必须按分子/骨架分组，不随机逐帧拆分。
- 同时报告能量和力；不能只挑 ANI-1x 优势最大的 COMP6 子集。
- README 的聚合值不是本次运行证据；逐构型预测、脚本、日志和配置必须保存。

## 证据交付

```text
reproduction/runs/A09/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── hardware.txt
├── comp6_files.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

不要提交完整 5.59 GB ANI-1x、上游仓库副本或受版权保护论文 PDF；只保存允许再分发
的配置、哈希、脚本和本次产生的结果。

## 停止条件

- T1 成功：固定 COMP6 子集可读，现代 ANI-1x 推理与误差管线可重复，单位正确。
- 停止并标 `blocked`：历史二进制/量化软件不可取得、论文 AL 参数或每轮数据无法
  解析、数据哈希不符、模型产生非有限能量/力或许可证不允许所需用途。
- 没有历史 Linux/CUDA/量化环境时保持 `offline-only`；现代 smoke 仍可完成。
- 只有论文版本、全部 AL 轮次、独立 COMP6 评价、Random 对照、日志和偏差齐全，
  才可标 `completed`。
