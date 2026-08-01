# 复现辅助工具

这些工具管理复现证据，不会代替论文代码，也不会自动把条目标为“完成”。

## 检查 32 个 recipe

```bash
python reproduction/tools/validate_recipes.py
```

检查内容包括：

- `manifest.json` 中是否正好覆盖全部独立论文卡和 W01–W07；
- ID、状态和文件路径是否一致；
- 每篇是否包含来源、环境、T0–T4、评价、证据与停止条件；
- README、论文卡和 recipe 的本地 Markdown 链接是否存在；
- 是否保留统一的 `reproduction/runs/<ID>/` 证据目的地；
- 没有实际运行证据时，是否有人误把状态写成 `completed`。

该命令只检查文档完整性，不访问网络，也不运行模型。

## 初始化一次真实运行

先预览：

```bash
python reproduction/tools/init_run.py A01 --dry-run
```

确认后创建：

```bash
python reproduction/tools/init_run.py A01
```

命令会创建来源锁定、日志、原始结果、处理结果、图表、论文对照和偏差记录模板。
已有文件不会被覆盖。环境和结果仍必须由实际命令产生，不能手填或复制论文数值。
