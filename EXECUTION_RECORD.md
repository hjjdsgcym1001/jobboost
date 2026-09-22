# 2. 执行记录

本文件用于记录仓库上传与三阶段质检的业务状态，便于定位失败原因。执行脚本后可将最新结果写入同目录的 `execution_log.json`。

## 业务状态

| 阶段 | 业务动作 | 状态判定 | 失败定位 |
|---|---|---|---|
| S0 | 仓库 ZIP 上传/解包 | 文件存在即可进入质检 | ZIP 无法读取或缺少项目根目录 |
| S1 | 1.2 准入检查 | 提交数量、代码规模、解析率、README 达到阈值 | 查看 admission checker 输出 |
| S2 | 1.3 Repo 质量检查 | 功能子系统、README/代码一致性、提交说明质量 | `scripts/repo_quality_check.py` |
| S3 | 1.5 Milestone 质量检查 | 聚合性、需求可验证性、代码覆盖、拆分粒度 | `scripts/repo_quality_check.py` 的 milestone 部分 |

## 执行命令

```bash
python scripts/admission_check.py
python scripts/repo_quality_check.py
python scripts/repo_quality_check.py --json
```

## 当前 ZIP 快照的已知限制

当前上传包不含 `.git` 目录，因此：

- 可以检查代码规模、解析率、README、功能子系统和 Milestone 代码覆盖；
- 无法从 ZIP 本身恢复真实 Commit 数量；
- 无法在 ZIP 本身可靠绑定具体 Commit SHA 区间；
- 回到原始 Git 仓库执行检查脚本后，Commit 相关字段会自动读取本地历史。

## 失败定位约定

- `PASS`：该检查项达到脚本定义的完整性条件。
- `WARN`：代码/文档存在但证据不足，或历史信息缺失。
- `UNAVAILABLE`：执行环境缺少必要输入（典型情况：没有 `.git`）。
- 脚本异常：优先检查 Python 版本、项目根目录和文件编码，再重新执行 JSON 模式。
