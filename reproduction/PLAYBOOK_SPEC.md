# 复现路径规范

本规范定义 `reproduction/recipes/<ID>/README.md` 的最低要求。`recipe`
表示“已写成可执行、可审计的复现路径”，不表示论文结果已经在本机复现。

## 状态语义

| 状态 | 含义 |
|---|---|
| `recipe-ready` | 来源、环境策略、命令入口、数据、指标与交付结构均已写明，可以开始执行 |
| `source-lock-needed` | 复现路径完整，但第一次运行前仍需把上游 ref 解析为 commit SHA |
| `reimplementation-only` | 没有可用作者代码，只能根据论文与公开数据重实现 |
| `offline-only` | 可以回放公开数据/结果，但完整实验需要仪器、HPC、DFT 或其他外部资源 |
| `blocked` | 当前缺少关键代码、数据、许可证或接口，不能诚实声称可执行 |
| `completed` | 已有固定来源、环境、命令、日志、原始结果、核对报告和偏差说明 |

只有实际运行证据齐全时才能使用 `completed`。

## 每个 recipe 必须包含

1. **定位与边界**
   - 论文/项目、分类、目标、是否属于 AL 或 BO；
   - 最小复现与完整复现的边界；
   - 普通电脑、GPU、HPC、仪器或 API 门槛。
2. **来源锁定**
   - DOI/正式论文；
   - 官方代码与数据；
   - clone/fetch 命令；
   - 第一次运行时记录 branch、tag、commit SHA、许可证和数据哈希的方法。
3. **环境**
   - 独立环境名称；
   - 优先使用的上游环境文件；
   - 环境导出与硬件记录方法；
   - 禁止凭猜测固定未核验的 Python/依赖版本。
4. **分层执行**
   - `T0`：只核验来源与入口；
   - `T1`：最小 smoke test；
   - `T2`：忠实复现论文主结果；
   - `T3`：统一协议重实现或消融；
   - `T4`：与粘合剂/DGEBA 课题的迁移（适用时）。
5. **公平性与评价**
   - 数据划分、初始集、预算、batch size、种子和重复次数；
   - Random/Greedy 等必要基线；
   - AL、BO、分类、势函数或物理模型各自正确的指标；
   - 数据泄漏、时间泄漏、结构泄漏和测试集偷看风险。
6. **证据交付**
   - `reproduction/runs/<ID>/source_lock.md`；
   - 环境文件、配置、日志、原始结果、处理后结果和图表；
   - `comparison.md` 与论文图表逐项核对；
   - `deviations.md` 记录所有修改、失败和未解决问题。
7. **停止条件**
   - 什么情况下算 smoke test 成功；
   - 什么情况下应停止并标记阻塞；
   - 什么证据齐全后才能把状态改为 `completed`。

## 统一运行目录

真正开始执行时建立：

```text
reproduction/runs/<ID>/
├── README.md
├── source_lock.md
├── environment.yml
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

可先预览或初始化这一结构：

```bash
python reproduction/tools/init_run.py A01 --dry-run
python reproduction/tools/init_run.py A01
```

初始化器只创建空白证据模板，不安装环境、不运行模型，也不修改实际执行状态。

上游代码统一放在本仓库之外：

```text
../upstream/<ID>-<short-name>/
```

不得把完整上游仓库、受版权保护的 PDF、没有再分发许可的数据或密钥提交到本仓库。

## 通用来源锁定命令

```bash
git clone <OFFICIAL_REPOSITORY_URL> ../upstream/<ID>-<short-name>
git -C ../upstream/<ID>-<short-name> remote -v
git -C ../upstream/<ID>-<short-name> branch --show-current
git -C ../upstream/<ID>-<short-name> describe --tags --always --dirty
git -C ../upstream/<ID>-<short-name> rev-parse HEAD
git -C ../upstream/<ID>-<short-name> status --short
```

将输出复制进 `reproduction/runs/<ID>/source_lock.md`。论文指定 tag、release
或 commit 时必须优先使用；未指定时记录访问日期和实际解析出的 SHA，不能只写
`main`、`master` 或 `latest`。
