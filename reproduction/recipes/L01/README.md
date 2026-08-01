# L01｜LLM-AL 免任务训练材料顺序推荐复现

**路径状态**：`offline-only`
**论文**：[Training-free active learning framework in materials science with large language models](https://doi.org/10.1038/s41524-026-02136-4)
**正式论文卡**：[`papers/related/goal_directed_al_bo/L01_LLM_AL_2026.md`](../../../papers/related/goal_directed_al_bo/L01_LLM_AL_2026.md)

## 定位与边界

LLM-AL 把已观测样本与候选范围放入提示，让 LLM 生成建议，再用 reranker 映射回离散候选池。四个任务均以尽快到达池中最优值为目标，所以这是**LLM 驱动的目标导向 AL/离散 BO**。

- 最小复现：不调用 API，读取官方已保存轨迹并重画 best-so-far/查询数。
- 忠实离线复现：重跑 Random、GPR/RF/XGB/BNN 基线，与保存的 LLM 轨迹比较。
- 在线近似复现：需要 OpenRouter/Claude 与 Cohere Rerank 商业 API、费用和网络；服务端模型会漂移。
- `training-free` 仅指不训练任务专用 LLM，不等于免费、无推理或确定性。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1038/s41524-026-02136-4`
- 官方代码和数据：[Toniaac/LLM-AL](https://github.com/Toniaac/LLM-AL)
- 上游无 tag/release，也未发现独立许可证文件；复制/改写代码前必须再次确认授权。
- 已核验 Notebook 使用 OpenAI-compatible OpenRouter client，模型 ID `anthropic/claude-3.7-sonnet`、`temperature=0.0`；Cohere `rerank-v3.5`；种子 38–42。模型 ID 不保证服务端权重冻结。

```bash
git clone https://github.com/Toniaac/LLM-AL.git ../upstream/L01-llm-al
git -C ../upstream/L01-llm-al remote -v
git -C ../upstream/L01-llm-al branch --show-current
git -C ../upstream/L01-llm-al describe --tags --always --dirty
git -C ../upstream/L01-llm-al rev-parse HEAD
git -C ../upstream/L01-llm-al status --short
find ../upstream/L01-llm-al -type f \
  \( -name '*.csv' -o -name '*.json' -o -name '*.ipynb' \) \
  -exec shasum -a 256 {} + | LC_ALL=C sort \
  > reproduction/runs/L01/data_sha256.txt
```

将 commit、无许可证风险、数据/轨迹清单和哈希写入 `reproduction/runs/L01/source_lock.md`。不得提交 API key 或原始带敏感信息的请求。

## 环境

上游没有环境文件。分成两个环境，均需在首次成功后锁定：

```bash
conda create -n repro-l01-offline python=3.11 pip jupyter -y
conda activate repro-l01-offline
python -m pip install numpy pandas matplotlib seaborn scipy scikit-learn \
  xgboost torch pyyaml
python -m pip freeze > reproduction/runs/L01/pip-freeze-offline.txt

conda create -n repro-l01-online python=3.11 pip jupyter -y
conda activate repro-l01-online
python -m pip install numpy pandas matplotlib seaborn pyyaml openai cohere
python -m pip freeze > reproduction/runs/L01/pip-freeze-online.txt
```

ML Notebook 还导入 `ibug`；安装来源和版本须由锁定 Notebook/包 metadata 解析后写入 `environment_resolution.md`。Python 3.11 是本项目选择，不是作者声明。

## T0｜数据、轨迹、提示和 API 核验

1. 固定 commit、数据/Notebook 哈希，记录无许可证文件这一限制。
2. 核对四个任务目标方向：steels/P3HT/membrane 最大化，perovskite 最小化（代码可能以负号统一最大化）。
3. 审计 Parameter/Report 两种 prompt、初始点、停止条件、候选映射和保存 CSV schema。
4. 核验模型、reranker、temperature、种子、runs；记录 OpenRouter/Cohere API 版本、价格、速率限制、数据保留政策。
5. 检查 Notebook 内 placeholder key 已保持占位符；真实 key 只能来自环境变量/密钥管理。

## T1｜最小 smoke test

完全离线：

1. 读取 `Sampling Performance Check/` 和 `al_trajectory_data_all/`。
2. 对每条轨迹验证候选索引存在、无重复、目标方向和停止点正确。
3. 重画一个数据集的 best-so-far 与到达全局最优查询数。
4. 用同一数据/seed 运行 Random 和 GPR-UCB 的小规模副本。

Smoke 成功要求：无需 API 即可从官方 CSV 重建一张轨迹图；每个点可回链到原数据；最小化方向未被反转。

## T2｜忠实复现论文主结果

离线可执行部分：

1. 运行 `Active Learning - Plotting.ipynb`、`Sampling Performance Analysis.ipynb` 对官方轨迹重算统计。
2. 运行 `Active Learning - ML-AL.ipynb` 的 GPR/RFR/XGB/BNN 和 Random，保持 alpha 列表 `[0,0.1,0.3,0.5,0.8,1,2,3,4,5]`、种子 38–42。
3. 比较两种 LLM 提示与传统基线的到达最优查询数/成功率。

在线生成仅在获授权预算后：

1. 用环境变量 `OPENROUTER_API_KEY`、`COHERE_API_KEY` 注入，先做单数据集/单 seed。
2. 保存完整 prompt、原始响应、候选文档顺序、reranker 返回、HTTP 时间、模型 ID、费用和错误/重试。
3. 与作者保存轨迹比较，但因云模型漂移，只称“当前服务近似复现”，不能要求逐点一致。

## T3｜统一协议与关键消融

- 使用完全相同初始候选、种子、预算和候选顺序比较 LLM、Random、GPR/RF/XGB/BNN-UCB。
- LLM 分离“生成建议”和“reranker 映射”；加入随机/最近邻映射对照。
- 消融 Parameter vs Report prompt、候选顺序、temperature、上下文长度和重复 API 调用。
- 报告到达最优的查询数、成功率、regret AUC、token/美元/延迟，并给失败解析率。
- 使用多个在线重复估计 API 非确定性，不能把 Python seed 当云模型 seed。

## T4｜迁移到 DGEBA/粘合剂数据

第一版只做高级基线：给 LLM 数值/文本数据字典和已观测真实实验，让其建议，再强制映射到化学组批准的离散候选池。LLM 不得生成候选池之外的危险或不可制备配方。

与 GP/RF/Random 在同预算比较，并记录 prompt 中是否泄露 Synthetic 标签生成规则。真实配方/未发表数据上传第三方 API 前必须获导师和数据所有者同意；否则仅使用公开/Synthetic 数据本地离线演练。

## 公平性与评价

- 主指标：到达池中最优/top 1% 的查询数、成功率、best-so-far、regret AUC。
- 成本：token、API 美元、rerank 次数、延迟和失败率；不能只报实验查询数。
- 所有方法共享初始点、预算、候选池和种子；LLM 服务端重复单独编号。
- 候选顺序、prompt 信息量、reranker 都可能形成额外优势，必须消融。
- 全池标签只用于事后评价；prompt 只能包含已查询标签。
- 传统基线超参不能用 LLM 已知结果反向选择。

## 证据交付

```text
reproduction/runs/L01/
├── README.md
├── source_lock.md
├── environment-offline.yml
├── environment-online.yml
├── environment_resolution.md
├── data_sha256.txt
├── api_manifest.md
├── configs/
├── prompts/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

API 原始响应可加密/脱敏；密钥永不落盘。`api_manifest.md` 记录供应商、模型、日期、价格和条款快照。

## 停止条件

- Smoke 成功：官方轨迹离线可解析、可回链，并重画至少一个任务与 Random/GPR 对照。
- 立即阻塞在线：无 API 授权/预算、模型 ID 下线、许可证/数据上传权不明、prompt 泄露未来标签。
- 离线论文图和基线齐全可标“offline reproduction completed”；只有锁定可用的在线调用、全部原始响应/成本/重复和论文核对齐全才可整体 `completed`，模型漂移需明确。
