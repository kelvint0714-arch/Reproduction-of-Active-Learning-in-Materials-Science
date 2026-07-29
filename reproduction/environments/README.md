# 论文环境管理

每篇论文使用独立环境，避免旧版 TensorFlow、PyTorch、JAX、GPy、MATLAB 或分子化学依赖互相冲突。

建议命名：

| 论文 | 环境名 |
|---|---|
| P01 | `al-p01-pvlab` |
| P02 | `al-p02-nist` |
| P03 | `al-p03-bgolearn` |
| P04 | `al-p04-neurobayes` |
| P05 | `al-p05-dkl-stm` |
| P06 | `al-p06-molpal` |
| P07 | MATLAB/MEX 独立记录 |
| P08 | `al-p08-camd` |
| P09 | 按 DP-GEN 官方容器或环境 |
| P10 | `al-p10-gpax` |

固定环境时至少记录：

- 操作系统与芯片；
- Python 版本；
- Conda/pip 锁定文件；
- CPU/GPU 与加速后端；
- 作者代码 commit；
- 我们的兼容性补丁；
- 最小验证命令。

这里以后保存**我们实际成功运行**的环境文件。未验证的依赖猜测不提交为可复现环境。
