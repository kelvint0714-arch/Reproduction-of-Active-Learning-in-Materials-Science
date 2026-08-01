# W03｜MOF 部分电荷 Dropout-GNN 主动学习复现路径

> 状态：`source-lock-needed`。预训练回放与完整 4-GPU AL 分层处理；未声称已运行。

## 定位与边界

- 论文：*Active learning graph neural networks for partial charge prediction of metal-organic frameworks via dropout Monte Carlo*，DOI：[10.1038/s41524-024-01277-8](https://doi.org/10.1038/s41524-024-01277-8)。
- 分类：GNN 不确定性 AL，不是 BO。Dropout Monte Carlo 选择结构，目标是减少达到部分电荷精度所需标签。
- 最小复现：CPU 回放作者预训练模型，在一个验证 MOF 上输出 8 次 dropout 预测与校准不确定性。
- 忠实复现：QMOF 离线标签池上运行 DMC-AL、Random、true-error oracle；完整脚本注明原实验用 4×RTX3090。
- 标签重算边界：论文用 VASP 6.2.1＋Chargemol DDEC；回放无需重跑 DFT，重新生成 oracle 需许可证/HPC。

## 来源锁定

- 作者代码、训练/验证数据和权重：[tummfm/mof-al](https://github.com/tummfm/mof-al)。
- QMOF 取得说明：[Andrew-S-Rosen/QMOF](https://github.com/Andrew-S-Rosen/QMOF)。
- ARC-MOF 结构：[Zenodo 10.5281/zenodo.10818822](https://doi.org/10.5281/zenodo.10818822)。
- 论文还注明 IZA 来源快照 `dc8a0295db`，需单独锁定。

```bash
git clone https://github.com/tummfm/mof-al.git ../upstream/W03-mof-al
git -C ../upstream/W03-mof-al remote -v
git -C ../upstream/W03-mof-al branch --show-current
git -C ../upstream/W03-mof-al describe --tags --always --dirty
git -C ../upstream/W03-mof-al rev-parse HEAD
git -C ../upstream/W03-mof-al status --short
shasum -a 256 ../upstream/W03-mof-al/data/*.pkl
```

记录 Apache-2.0、每个 pickle 的大小/哈希及受限 DFT 工具信息于 `reproduction/runs/W03/source_lock.md`。不要反序列化未知来源 pickle；只使用锁定官方文件并在隔离环境读取。

## 环境

- 环境名：`repro-W03`。
- 作者 `setup.py` 固定 JAX 0.3.14、jax-md 0.1.28、Haiku 0.0.6 等，并给出旧 CUDA wheel；优先 Linux/兼容 CUDA 容器。

```bash
mamba create -n repro-W03 python=3.9 pip -y
mamba activate repro-W03
python -m pip install -e ../upstream/W03-mof-al
python -m pip install "jax[cuda]==0.3.14" \
  -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
python -m pip freeze > /ABS/PATH/reproduction/runs/W03/pip-freeze.txt
conda env export --from-history > /ABS/PATH/reproduction/runs/W03/environment.from-history.yml
```

CPU smoke 需安装相同 JAX 的 CPU wheel；若已从 PyPI 装好，不再装 CUDA 行。记录 Python/JAX/CUDA/驱动/GPU 型号。

## T0｜来源与入口核验

1. 核对 `run_trained_model.py`、`data_preprocessing.py`、`active_learning.py` 与三个 pickle。
2. 从源码锁定：held-out 20%、initial train 1%、AL batch 16、每次 4 个新样本、dropout 0.1、8 次采样、初训 1000 epochs。
3. 注意 `active_learning.py` 连续赋值 `al_case`，最终默认是 `UQ`；Random/oracle 必须复制脚本后明确设定，不能以为三者会一次运行。
4. 预处理生成 `train_data.pkl`/`test_data.pkl`，并锁哈希。

## T1｜最小 smoke test

```bash
cd ../upstream/W03-mof-al
CUDA_VISIBLE_DEVICES="" python run_trained_model.py \
  > /ABS/PATH/reproduction/runs/W03/logs/pretrained-smoke.log 2>&1
```

成功标准：输出 dropout 预测数组 shape，无 NaN/异常；在运行副本中追加保存 mean、未校准/校准 std 和数据 ID。只打印 shape 仍仅算“入口 smoke”。

## T2｜忠实复现论文主结果

1. 运行 `data_preprocessing.py`；验证小 MOF/大 MOF/未知元素过滤数量。
2. 在 `runs/W03/src/` 复制三份 AL 脚本，分别固定 `UQ`、`random`、`true_error`；禁止修改上游。
3. 使用论文硬件/等效资源跑相同初始索引、batch 和训练 schedule，保存 checkpoint、labeled/pool 索引、MAE/SMAE history。
4. 复现 Fig. 3：达到 SMAE 精度目标时 DMC/Random/oracle 所需训练比例，并核对 MAE 上 AL 优势可能不明显。
5. 回放 ARC-MOF/IZA/大 MOF，报告 MAE、SMAE、不确定性校准和 OOD 过度自信。

## T3｜统一协议与消融

- 相同初始/预算比较 DMC、Random、oracle；oracle 只作不可部署上限。
- 消融 dropout 概率、采样次数 8、校准系数、batch size；同时报告精度与校准。
- 按结构数据库/拓扑/元素分组 OOD，检查未知元素的失败模式。

## T4｜迁移至 DGEBA

- 只有构建合理的分子/配方图和真实标签后才考虑 GNN；当前表格先用 RF/GP/DAGS。
- 可将 DMC 思路用于小型 MLP/GNN：每轮选预测标准差大的配方；结构对分组测试。
- 保存未知元素/新官能团覆盖检查；模型外元素不得给出低不确定性结论。

## 公平性与评价

- 主指标：SMAE 与达到目标的标签比例；辅指标：MAE、每 MOF MAE、误差—不确定性相关、校准覆盖率。
- DMC/Random/oracle 共用 held-out/初始索引/预算/schedule；论文基线不可少。
- 以 MOF 为单位拆分，不能让同一结构的原子跨训练/测试；未知元素单列。
- true-error 采集读取池真值，只能称 oracle；测试集和 OOD 验证集不得参与选点。

## 证据交付

```text
reproduction/runs/W03/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── configs/
├── src/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

必须保存 labeled/pool 索引、checkpoint、硬件/时长和 pickle 哈希。

## 停止条件

- smoke 成功：预训练模型对官方验证数据完成 8 次 dropout 推断。
- 停止：旧 JAX/CUDA 无法解析且无容器、pickle/hash 不符、三基线初始索引不同、oracle 被写成可部署方法、OOM 后改变 batch 未记录。
- 固定环境、三策略完整轨迹、Fig. 3/OOD 核对和偏差齐全才可 `completed`；未重跑 VASP 时只声明 ML 回放完成。
