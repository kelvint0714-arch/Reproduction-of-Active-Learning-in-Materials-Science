# S01｜复合材料热化学固化 PINN 论文重实现

**路径状态**：`reimplementation-only`
**论文**：[Physics-informed neural network for modelling the thermochemical curing process of composite-tool systems during manufacture](https://doi.org/10.1016/j.cma.2021.113959)
**正式论文卡**：[`papers/supporting/physics_modeling/S01_Thermochemical_Curing_PINN.md`](../../../papers/supporting/physics_modeling/S01_Thermochemical_Curing_PINN.md)

## 定位与边界

论文用解耦神经网络求解复合材料—模具系统的热传导 PDE 与树脂固化动力学 ODE，并处理界面不连续。它是**物理建模/PINN**，原论文没有候选池、采集函数或回填循环，因此不是主动学习。

- 最小重实现：论文最简单 1D 案例，与独立有限差分/有限元参考解比较。
- 忠实重实现：按论文所有方程、边界/界面、顺序训练、自适应损失和案例重建。
- 未发现可确认的作者官方代码/固定环境；不能声称“运行作者代码”。
- 1D smoke 普通电脑可运行；论文全部网络、超参重复建议 GPU。

## 来源锁定

一手来源：

- 正式论文 DOI：`10.1016/j.cma.2021.113959`
- 作者预印本：[arXiv:2011.13511](https://arxiv.org/abs/2011.13511)
- 截至本 recipe 核验日期，无论文明确指向的官方代码仓库。

```bash
mkdir -p ../upstream/S01-thermochemical-pinn
curl -L 'https://arxiv.org/pdf/2011.13511' \
  -o ../upstream/S01-thermochemical-pinn/arxiv-2011.13511.pdf
shasum -a 256 ../upstream/S01-thermochemical-pinn/arxiv-2011.13511.pdf
curl -L 'https://export.arxiv.org/api/query?id_list=2011.13511' \
  -o ../upstream/S01-thermochemical-pinn/arxiv-metadata.xml
shasum -a 256 ../upstream/S01-thermochemical-pinn/arxiv-metadata.xml
```

PDF 不提交仓库。把 DOI、arXiv version/date/hash、代码检索范围和“无官方代码”结论写入 `reproduction/runs/S01/source_lock.md`。

## 环境

环境名：`repro-s01-curing-pinn`。以下是本项目 PyTorch 重实现环境，不是作者环境；首次可运行后锁定完整版本：

```bash
conda create -n repro-s01-curing-pinn python=3.11 pip -y
conda activate repro-s01-curing-pinn
python -m pip install torch numpy scipy pandas matplotlib pyyaml
python -m pip check
python -m pip freeze > reproduction/runs/S01/pip-freeze.txt
conda env export --no-builds > reproduction/runs/S01/environment.yml
```

若论文明确使用另一框架，以论文为准；框架差异写入 `deviations.md`。有限差分参考解必须独立于 PINN 自动微分实现。

## T0｜方程、参数与案例规范化

1. 从正式论文/补充材料逐字转录热传导、固化动力学、热源、初始/边界与复合材料—模具界面连续条件，保留方程号。
2. 建立 `equations.md` 和 `parameter_table.csv`，记录单位、数值、来源页码及未报告项；不猜缺失参数。
3. 建立 `case_matrix.md`：几何、厚度、固化循环、网络、采样点、训练顺序、损失权重和论文图。
4. 实现量纲/无量纲检查和独立 FD/FEM 参考解。
5. 列出论文未公开的 seed、初始化或优化器细节，定义可接受的重实现偏差。

## T1｜最小 smoke test

选择论文最简单 1D 均匀材料/边界案例：

1. 先运行 FD/FEM 网格收敛，保存至少三档网格。
2. PINN 只训练少量 collocation points，验证温度、固化度输出范围与物理残差有限。
3. 检查初始/边界条件、界面温度和热流连续性。
4. 固定 3 个 seed，确保 loss 降低且无 NaN。

Smoke 成功不要求达到论文精度，只要求方程、单位、边界和数据管线正确。任何简化均写入 `configs/smoke.yaml`。

## T2｜忠实重实现论文主结果

1. 恢复论文网络、collocation、优化器、顺序训练与自适应损失。
2. 按论文案例逐一训练温度网络和固化度网络。
3. 用论文指定的边界/固化循环和独立数值解生成参考。
4. 保存每项 PDE/ODE/BC/IC/interface loss、场预测、训练时间与 seed。
5. 重画温度—时间、固化度—时间、空间场和误差图，逐项核对论文。
6. 未报告超参使用预先注册的搜索范围，结果写为重实现，不称精确复现。

## T3｜统一协议与消融

- 普通 PINN、顺序训练、自适应损失、去掉界面处理四组比较。
- 对 collocation 数、网络宽深、温度缩放、optimizer 和 loss 权重做消融。
- 与 FD/FEM 在同案例比较误差、训练/推理时间和能量守恒。
- 在未见厚度/固化循环上测试外推。
- 报告 5 个以上 seed，避免仅展示最优网络。

## T4｜迁移到 DGEBA/粘合剂数据

若课题关心固化温度场/固化度，S01 可作为物理代理或生成物理特征；它不能直接从分子结构预测剪切强度，也不自带主动学习。先由化学组给出可信的热物性、固化动力学和边界条件。

若接 AL/BO，另建候选固化工艺、预测不确定性和采集函数，让新实验回填；这属于新扩展。必须与纯 GP/RF、无 PINN 物理特征基线比较。

## 公平性与评价

- 场误差：relative \(L_2\)、RMSE、最大绝对误差，温度和固化度分别报告。
- 物理：PDE/ODE 残差、边界/初始/界面残差、能量平衡误差。
- 效率：训练时间、推理时间、显存/内存与 collocation 数。
- 所有方法共享参考解、训练/测试工况和 seed；网格收敛必须先于模型比较。
- 不在测试工况上调损失权重；不可用 PINN 自己生成的解作为唯一真值。
- 原论文没有 AL 指标，不应附会 top-k/regret。

## 证据交付

```text
reproduction/runs/S01/
├── README.md
├── source_lock.md
├── environment.yml
├── pip-freeze.txt
├── equations.md
├── parameter_table.csv
├── case_matrix.md
├── configs/
├── logs/
├── raw_results/
├── processed_results/
├── figures/
├── comparison.md
└── deviations.md
```

另保存 FD/FEM 网格收敛表、模型 checkpoint、每项 loss 和全部 seeds。

## 停止条件

- Smoke 成功：独立参考解收敛，PINN 无 NaN，边界/界面满足且最简单案例误差可计算。
- 立即阻塞：关键方程/单位/边界或参数缺失且无法从论文确认、参考解不收敛、框架修正改变物理问题。
- 只有论文全部案例、参考解、多个 seed、物理残差、论文图核对和偏差齐全，才能把状态从 `reimplementation-only` 改为 `completed`（并继续注明无作者代码）。
