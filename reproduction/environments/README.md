# 论文环境管理

每篇论文使用独立环境，避免旧版 TensorFlow、PyTorch、JAX、GPy、MATLAB 或分子化学依赖互相冲突。

建议命名：

| 论文 | 环境名 |
|---|---|
| A01 | `al-a01-nist-structure-property` |
| A02 | `al-a02-dags` |
| A03 | `al-a03-benchmark-mat` |
| A05 | `al-a05-gp-net` |
| A08 | `al-a08-aiphad` |
| P04 | `al-p04-neurobayes` |
| P05 | `al-p05-dkl-stm` |
| P07 | MATLAB/MEX 独立记录 |
| P09 | 按 DP-GEN 官方容器或环境 |
| P01（BO） | `bo-p01-pvlab` |
| P02（BO） | `bo-p02-nist` |
| P03（BO） | `bo-p03-bgolearn` |
| P06（分子 BO） | `bo-p06-molpal` |
| P08（平台） | `platform-p08-camd` |
| P10（BO） | `bo-p10-gpax` |

固定环境时至少记录：

- 操作系统与芯片；
- Python 版本；
- Conda/pip 锁定文件；
- CPU/GPU 与加速后端；
- 作者代码 commit；
- 我们的兼容性补丁；
- 最小验证命令。

这里以后保存**我们实际成功运行**的环境文件。未验证的依赖猜测不提交为可复现环境。
