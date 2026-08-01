# P07｜CAMEO 闭环材料发现复现路径

> 状态：`recipe-ready`、`offline-only`。可回放公开 Fe–Ga–Pd 算法与数据；无法在
> 普通电脑上复现同步辐射/XRD 和材料制备闭环。

## 定位与边界

- 论文：*On-the-fly closed-loop materials discovery via Bayesian active learning*，
  Nature Communications 11, 5966 (2020)，DOI：<https://doi.org/10.1038/s41467-020-19597-w>。
- 分类：相图学习阶段属于模型/知识学习型 AL；相区内寻找目标性能包含 BO。不能把
  CAMEO 简化描述成单一 GP+UCB。
- 最小复现：在 MATLAB 中编译 Graph Cut MEX，载入仓库数据并启动
  `running scripts/FeGaPd_ALBO_200801a.m` 的离线模拟。
- 忠实离线复现：保存每轮测量点、相区推断、相图误差/知识变化和目标发现轨迹。
- 完整真实闭环需要组合材料样品、同步辐射/实验室 XRD、仪器通信、人工监督和安全
  流程，永久标记 `offline-only`，除非确有对应设施与原始实验日志。

## 来源锁定

- 正式论文：Nature DOI 页面。
- 作者仓库：<https://github.com/KusneNIST/CAMEO_NComm>。
- 固定归档：Zenodo v1，DOI <https://doi.org/10.5281/zenodo.3998288>。
- Zenodo 文件 `KusneNIST/CAMEO_NComm-v0.1.zip`，记录给出的 MD5 为
  `9c7db1eb5a4b1a11af26a767f950f214`；GitHub tag `v0.1` 对应 commit
  `62a1264ff528ad318748070e0a3568fc020e62f4`。
- README 含 NIST 公共服务/美国政府作品许可声明；仍须保存原声明，且不能推定第三方
  MEX 或数据拥有相同许可。

```bash
git clone --branch v0.1 --single-branch \
  https://github.com/KusneNIST/CAMEO_NComm.git \
  ../upstream/P07-cameo
git -C ../upstream/P07-cameo remote -v
git -C ../upstream/P07-cameo branch --show-current
git -C ../upstream/P07-cameo describe --tags --always --dirty
git -C ../upstream/P07-cameo rev-parse HEAD
git -C ../upstream/P07-cameo status --short
test "$(git -C ../upstream/P07-cameo rev-parse HEAD)" = \
  "62a1264ff528ad318748070e0a3568fc020e62f4"
```

归档下载和核验：

```bash
curl -L \
  https://zenodo.org/api/records/3998288/files/KusneNIST%2FCAMEO_NComm-v0.1.zip/content \
  -o reproduction/runs/P07/raw_results/CAMEO_NComm-v0.1.zip
md5 reproduction/runs/P07/raw_results/CAMEO_NComm-v0.1.zip
shasum -a 256 reproduction/runs/P07/raw_results/CAMEO_NComm-v0.1.zip \
  > reproduction/runs/P07/data_sha256.txt
```

把 Zenodo 元数据 JSON、访问日期、Git SHA、MATLAB/MEX 文件哈希和许可声明写入
`source_lock.md`；归档若不允许再分发则不提交。

## 环境

环境名建议 `al-p07-cameo-matlab`。上游没有现代环境锁；使用本机 MATLAB 与受支持
C++ 编译器，记录实际版本，禁止猜测论文使用版本。

```bash
matlab -batch "disp(version); disp(computer); mex -setup C++" \
  > reproduction/runs/P07/hardware.txt
```

Graph Cut 位于 `Graph Cut mex2.0/`。若 MATLAB/MEX 不可用，T0 仍可完成，但 T1
标 `blocked`；Octave 兼容性未经上游声明，不得把 Octave 结果当忠实复现，若尝试只
能列入 T3 和 `deviations.md`。

## T0｜来源和入口核验

```bash
test -f "../upstream/P07-cameo/running scripts/FeGaPd_ALBO_200801a.m"
test -f "../upstream/P07-cameo/Graph Cut mex2.0/compile_gc.m"
find ../upstream/P07-cameo/data -type f -print0 |
  sort -z | xargs -0 shasum -a 256 \
  > reproduction/runs/P07/data_files_sha256.txt
```

成功标准：commit、Zenodo checksum、入口脚本、data、shared 和 Graph Cut 源文件均
存在；记录脚本中的随机数设置、相图 ground truth 和输出目录。

## T1｜最小离线回放

先编译 MEX，再运行官方入口；命令从上游根目录启动，以保留相对路径：

```bash
matlab -batch "cd('../upstream/P07-cameo'); \
addpath(genpath(pwd)); \
cd('Graph Cut mex2.0'); compile_gc; cd('..'); \
cd('running scripts'); FeGaPd_ALBO_200801a" \
  2>&1 | tee reproduction/runs/P07/logs/t1_cameo.log
```

若完整脚本耗时过长，只可在 `configs/` 中保存一份缩短迭代数的副本做 smoke test，
并记录行级 diff；不得改上游。成功标准：数据加载、Graph Cut 调用、至少一次
“选点→oracle 查询→相图更新”完成，选择点合法且输出无 NaN。

## T2｜忠实复现论文主结果

1. 使用 v0.1 原入口和原数据，锁定 MATLAB RNG 状态；不缩短预算。
2. 保存每轮已测成分、候选评分、相标签、相边界、性能代理预测与下一点。
3. 分别报告相图学习和目标性质优化，不能把两者的预算/指标混为一条曲线。
4. 复现论文 Fe–Ga–Pd 离线基准，逐图核对“测量数—相图质量/知识增益”和目标区域
   发现；论文声称的约 10 倍实验减少应从相同定义重算，不能直接抄摘要。
5. Ge–Sb–Te 的真实在线过程只能利用已公开轨迹做离线回放；没有仪器日志时明确
   “未复现实验控制”。

## T3｜统一协议重实现或消融

- 同一初始点、预算和 RNG 下比较 Random、无物理先验 CAMEO、完整 CAMEO。
- 分别关闭相律/物理先验、图传播、相边界偏置和目标性能项，观察相区错误与发现效率。
- 指标：相标签 balanced accuracy/ARI（按数据允许）、边界距离、整图误分类风险、
  每轮知识增益、目标发现预算和墙钟时间。
- 先忠实回放 MATLAB，再考虑 Python 重实现；Python 结果必须作为新实现，不得覆盖
  官方结果。
- 所有超参数只用训练/验证轨迹选择，最终留出相图不得用于调采集策略。

## T4｜迁移到粘合剂 / DGEBA

- 可迁移的是“领域约束参与选样”：例如配比和为 100%、可制造范围、固化窗口、
  相容性/相分离规则、实验安全与成本。
- 把配方空间建成图时，边连接必须来自预先定义的结构/配比邻域，不得根据目标标签
  事后连边。
- 第一阶段 AL 学习整个配方—性能映射或可行域；第二阶段才在可靠可行域内做 BO。
- 当前每个离子液体/多酚结构对只出现一个配比，不能套 CAMEO 曲面后声称得到连续
  配比峰谷；需先设计固定结构对的配比序列实验。

## 公平性与评价

- 固定初始点、候选图、总预算、batch size、随机种子和 oracle；Random 使用同一
  初始点且重复多次。
- 相图指标和性能优化指标分别报告；不能用最佳性能掩盖相图整体学习失败。
- 物理先验必须在查询标签前定义；从完整相图提取的边界信息属于泄漏。
- 离线 oracle 的标签一次只向策略暴露被查询点；测试相图只用于评估。
- 报告 MATLAB/OS/MEX 编译器差异和随机性，不只给最终图。

## 证据交付

```text
reproduction/runs/P07/
├── README.md
├── source_lock.md
├── environment.yml
├── hardware.txt
├── data_sha256.txt
├── data_files_sha256.txt
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

交付每轮点位/标签/相图、消融结果、运行成本和论文逐图核对。真实仪器需要另附仪器
配置、校准、故障和人工干预日志；本离线 recipe 不生成或伪造这些证据。

## 停止条件

- T1 成功：锁定数据可读、MEX 编译成功、至少一轮离线闭环完成并产生可审计输出。
- 停止并标 `blocked`：v0.1/Zenodo 哈希不符、MEX 无法在记录的编译器上构建、
  关键数据缺失或脚本要求未公开接口。
- 没有同步辐射/样品只意味着保持 `offline-only`，不得把离线模拟描述为真实发现。
- 只有来源/数据/环境/日志、完整预算结果、基线与消融、逐图核对和偏差全部齐全，
  才能把“离线算法复现”状态改为 `completed`。
