# A05｜GP-Net 熵主动学习 GNN 代理复现路径

> 状态：`source-lock-needed`。优先回放已发布潜在向量，再处理旧 TensorFlow/MEGNet 环境；未声称已运行。

## 定位与边界

- 论文：*Entropy-based Active Learning of Graph Neural Network Surrogate Models for Materials Properties*，DOI：[10.1063/5.0065694](https://doi.org/10.1063/5.0065694)。
- 分类：模型学习型 AL，不是 BO。MEGNet 产生晶体嵌入，Laplacian-kernel GP 提供预测与熵。
- 最小复现：固定 Zenodo 潜在向量，比较 Random 与 entropy 的形成能 MAE 学习曲线。
- 忠实复现：恢复 MEGNet 编码、固定 1,460 个测试材料并重训/重复 AL。
- 门槛：回放可 CPU；旧环境是 Linux/Python 3.7/TensorFlow 2.1/CUDA 10.1，完整训练需兼容 GPU 或容器。

## 来源锁定

- 作者代码：[mdi-group/gp-net](https://github.com/mdi-group/gp-net)。
- 论文实验包：[Zenodo 10.5281/zenodo.4922828](https://doi.org/10.5281/zenodo.4922828)。
- 作者仓库有 `1.0.0` tag，优先固定此 tag：

```bash
git clone https://github.com/mdi-group/gp-net.git ../upstream/A05-gp-net
git -C ../upstream/A05-gp-net fetch --tags --force
git -C ../upstream/A05-gp-net checkout --detach 1.0.0
git -C ../upstream/A05-gp-net remote -v
git -C ../upstream/A05-gp-net describe --tags --always --dirty
git -C ../upstream/A05-gp-net rev-parse HEAD
git -C ../upstream/A05-gp-net status --short
```

从 Zenodo API 保存清单；至少下载并核对 `yvals_latent.npy`、`latent_test.npy`、`ytest.npy`、`samp_indices.npy`、`gp_mae_random.npy`、`gp_mae_entropy.npy`。归档公布的 MD5 必须与本地一致，另生成 SHA-256，写入 `reproduction/runs/A05/source_lock.md`。

## 环境

- 环境名：`repro-A05-replay`（潜在向量回放）和 `repro-A05-full`（作者旧环境）。
- 回放环境只装 NumPy/SciPy/scikit-learn/pandas/matplotlib；完整环境优先 `gp-megnet.yml`，不要在 Apple Silicon 原样强装 GPU 构建。

```bash
mamba env create -n repro-A05-full -f ../upstream/A05-gp-net/gp-megnet.yml
mamba activate repro-A05-full
python ../upstream/A05-gp-net/gp-net.py --help
conda env export --from-history > /ABS/PATH/reproduction/runs/A05/environment.from-history.yml
conda list --explicit > /ABS/PATH/reproduction/runs/A05/environment.explicit.txt
```

若改用容器，记录镜像 digest、CUDA/驱动；环境迁移不得悄悄替换 GP 核或 MEGNet 层。

## T0｜来源与入口核验

1. 核对 tag、`gp-megnet.yml`、`gp-net.py`、`paper/notebooks/active-learning.ipynb`。
2. 将 Zenodo API 文件名、大小、MD5 全量保存；确认测试集向量/标签行数一致。
3. 对照 CLI：`-samp random|entropy`、`-cycle`、`-q`、`-stop`、`-nomeg`，写入配置快照。

## T1｜最小 smoke test

1. 先打开 Zenodo 的 `active-learning-new.ipynb`，把数据路径改为只读归档目录。
2. 使用固定潜在向量和标签，单个种子、少量初始点、5 次采集分别跑 Random/entropy。
3. 保存查询索引、GP 均值/标准差、每轮测试 MAE。

成功标准：两策略均产生 5 轮、预测维度与 1,460 个测试标签一致、entropy 只使用训练后验不确定性。不要用归档的成品 `gp_mae_*.npy` 代替计算 smoke。

## T2｜忠实复现论文主结果

1. 使用 Zenodo `paper-experiments.tgz` 中固定拆分/嵌入和论文命令，复现 Random 与 entropy 多次学习曲线。
2. 核对固定测试集 MAE、MSE、\(R^2\)、预测区间校准和误差带。
3. 先以归档潜在向量对齐结果；随后才恢复 `gp-megnet.yml` 并训练/提取 MEGNet `readout_0` 嵌入。
4. 分开报告“GP 回放”和“MEGNet+GP 端到端”，不得用前者声称已重训 GNN。

## T3｜统一协议与消融

- 相同初始集/预算下对比 Random、entropy；增加不同 GP 核/固定核参数消融。
- 表征消融：归档嵌入、随机嵌入、简单组成描述符；测试集不参与缩放或嵌入选择。
- 保存每轮采集熵、实际绝对误差，检查不确定性校准而不只看最终 MAE。

## T4｜迁移至 DGEBA

- 结构输入可先用 ECFP/数值描述符代替晶体 MEGNet；GP 对低维嵌入做熵采样。
- 按结构对分组留出；Random 与 entropy 共用初始样本，先预测 Y1。
- 后续若用 GNN，输入必须是可验证分子/配方图，不能把表格行伪装成论文晶体图。

## 公平性与评价

- 主指标：固定测试 MAE—标签数；辅指标：MSE、\(R^2\)、校准误差、误差—标准差相关性、学习曲线 AUC。
- Random 必须存在；初始索引、预算、GP 超参数和重复种子完全一致。
- 测试集 1,460 条必须隔离；MEGNet 预训练数据若与测试材料重叠，要在 `deviations.md` 说明表示预训练泄漏风险。

## 证据交付

```text
reproduction/runs/A05/
├── README.md
├── source_lock.md
├── environment.from-history.yml
├── environment.explicit.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

保存 Zenodo manifest、嵌入哈希、查询索引和端到端/回放两套比较。

## 停止条件

- smoke 成功：固定嵌入上 Random/entropy 均完成并输出测试 MAE。
- 停止：归档哈希不符、测试/训练索引重叠、旧环境无法建立却未记录迁移、成品数组被误当重算结果。
- 只有固定 tag/数据、两层实验、重复结果和论文图表核对齐全才可 `completed`。
