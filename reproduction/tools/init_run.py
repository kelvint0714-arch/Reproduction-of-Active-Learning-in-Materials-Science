#!/usr/bin/env python3
"""Create an evidence directory for one reproduction recipe.

The generated files are blank audit scaffolding. This command never installs an
environment, runs upstream code, or changes an item's execution status.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "reproduction" / "manifest.json"
RUNS_ROOT = REPO_ROOT / "reproduction" / "runs"
RESULT_DIRECTORIES = (
    "configs",
    "logs",
    "raw_results",
    "processed_results",
    "figures",
)


def load_entry(paper_id: str) -> dict[str, str]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in manifest["entries"]}
    try:
        return entries[paper_id]
    except KeyError as error:
        choices = ", ".join(entries)
        raise SystemExit(
            f"Unknown ID {paper_id!r}. Choose one of: {choices}"
        ) from error


def write_once(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def initialize_run(entry: dict[str, str], dry_run: bool) -> Path:
    paper_id = entry["id"]
    run_dir = RUNS_ROOT / paper_id
    planned = [
        run_dir,
        *(run_dir / name for name in RESULT_DIRECTORIES),
        run_dir / "README.md",
        run_dir / "source_lock.md",
        run_dir / "comparison.md",
        run_dir / "deviations.md",
    ]
    if dry_run:
        print("\n".join(str(path.relative_to(REPO_ROOT)) for path in planned))
        return run_dir

    run_dir.mkdir(parents=True, exist_ok=True)
    for name in RESULT_DIRECTORIES:
        (run_dir / name).mkdir(exist_ok=True)

    recipe_link = f"../../recipes/{paper_id}/README.md"
    card_link = f"../../../{entry['card']}"
    write_once(
        run_dir / "README.md",
        f"""# {paper_id} 复现运行证据

- 项目：{entry["title"]}
- 创建日期：{date.today().isoformat()}
- 执行状态：`not_started`
- recipe：[{paper_id}]({recipe_link})
- 论文卡：[来源卡]({card_link})

## 本次范围

- 目标层级：T0 / T1 / T2 / T3 / T4（保留实际执行项）
- 数据：
- 方法：
- 预算：
- 种子：
- 硬件：

## 可重放命令

```bash
# 在实际运行后填写；不得只写“运行 notebook”。
```

## 产物索引

- 配置：`configs/`
- 日志：`logs/`
- 原始结果：`raw_results/`
- 处理结果：`processed_results/`
- 图表：`figures/`
- 来源锁定：`source_lock.md`
- 论文核对：`comparison.md`
- 偏差记录：`deviations.md`
""",
    )
    write_once(
        run_dir / "source_lock.md",
        f"""# {paper_id} 来源锁定

- 论文 DOI/正式页面：
- 上游代码 URL：
- 上游 commit SHA：
- branch/tag：
- 许可证及版本：
- 数据 URL/DOI：
- 数据版本：
- 数据文件哈希：
- 锁定日期：

## 锁定命令与原始输出

```bash
git remote -v
git branch --show-current
git describe --tags --always --dirty
git rev-parse HEAD
git status --short
```

不要只记录 `main`、`master` 或 `latest`；必须保存实际 SHA。
""",
    )
    write_once(
        run_dir / "comparison.md",
        f"""# {paper_id} 与论文结果对照

| 论文图/表 | 论文设置 | 本地设置 | 论文值/趋势 | 本地值/趋势 | 结论 |
|---|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 未核验 |

允许的结论只有：`相符`、`部分相符`、`不相符`、`无法核验`。每一项必须链接到
原始日志或结果文件。
""",
    )
    write_once(
        run_dir / "deviations.md",
        f"""# {paper_id} 偏差与阻塞

| 日期 | 层级 | 原论文/上游设置 | 本地变化或失败 | 原因 | 对结论的影响 |
|---|---|---|---|---|---|
| 待填写 | T0–T4 | 待填写 | 待填写 | 待填写 | 待评估 |

失败运行也应保留命令、日志和环境信息，不得删除后只记录成功尝试。
""",
    )
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize an auditable run directory for one paper ID."
    )
    parser.add_argument("paper_id", help="Manifest ID, for example A01 or P03")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the paths without creating files",
    )
    args = parser.parse_args()

    paper_id = args.paper_id.upper()
    entry = load_entry(paper_id)
    run_dir = initialize_run(entry, args.dry_run)
    verb = "Would initialize" if args.dry_run else "Initialized"
    print(f"{verb}: {run_dir.relative_to(REPO_ROOT)}")
    if not args.dry_run:
        print("Execution status was not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
